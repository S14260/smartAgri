// 全局变量
let map;               // 地图实例
let drawnItems;        // 用户绘制图层集合
let heatLayer;         // 热力图图层，避免重复创建
let currentNdviLayer = null;
let currentNdviTime = null;
const ndviCache = {};  // 缓存 { timeKey: georaster }


const ndviTifMap = {
    "2024-08-18": "http://123.56.228.32/0818_NDVI.tif",
    "2024-08-20": "http://123.56.228.32/0820_NDVI.tif",
    "2024-08-23": "http://123.56.228.32/0823_NDVI.tif",
    "2024-08-25": "http://123.56.228.32/0825_NDVI.tif"

};document.addEventListener("DOMContentLoaded", () => {
    initMap();
    loadPlots();
    setupSearch();

    const timeKeys = Object.keys(ndviTifMap);
    const buttonContainer = document.getElementById("ndviTimeButtons");

    // 自动渲染时间按钮
    timeKeys.forEach(time => {
        const btn = document.createElement("button");
        btn.textContent = time;
        btn.className = "layui-btn layui-btn-sm layui-btn-primary";  // 默认样式

        btn.addEventListener("click", () => {
            if (time === currentNdviTime) return;

            currentNdviTime = time;
            const tifUrl = ndviTifMap[time];

            // 显示加载提示
            showCustomMsg("正在加载 NDVI 图层，请稍候...");


            // 高亮当前按钮
            document.querySelectorAll("#ndviTimeButtons button").forEach(b => {
                b.classList.remove("layui-btn-normal");
                b.classList.add("layui-btn-primary");
            });
            btn.classList.remove("layui-btn-primary");
            btn.classList.add("layui-btn-normal");

            // 移除旧图层
            if (currentNdviLayer) {
                map.removeLayer(currentNdviLayer);
            }

            // 加载或使用缓存
            if (ndviCache[time]) {
                const cachedRaster = ndviCache[time];
                currentNdviLayer = new GeoRasterLayer({
                    georaster: cachedRaster,
                    opacity: 0.7,
                    resolution: 256,
                    pixelValuesToColorFn: pixelToColor
                });
                currentNdviLayer.addTo(map);
                console.log("NDVI图层已加载");
                showCustomMsg("✅ NDVI 图层加载完成");
            } else {
                fetch(tifUrl)
                    .then(res => res.arrayBuffer())
                    .then(parseGeoraster)
                    .then(georaster => {
                        ndviCache[time] = georaster;
                        currentNdviLayer = new GeoRasterLayer({
                            georaster,
                            opacity: 0.7,
                            resolution: 256,
                            pixelValuesToColorFn: pixelToColor
                        });
                        currentNdviLayer.addTo(map);
                        console.log("NDVI图层已加载");
                        showCustomMsg("✅ NDVI 图层加载完成");
                    })
                    .catch(err => {
                        console.error("加载 NDVI 图层失败：", err);
                        alert("❌ NDVI 加载失败：" + err.message);
                    });
            }
        });

        buttonContainer.appendChild(btn);
    });


    // 切换 NDVI 控件显示/隐藏
    ["toggleSliderBtn", "toggleSliderBtnMobile"].forEach(id => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.addEventListener("click", () => {
                const wrapper = document.getElementById("ndviSliderWrapper");
                const isHidden = getComputedStyle(wrapper).display === "none";
                wrapper.style.display = isHidden ? "block" : "none";
            });
        }
    });

});

// NDVI 像素值转颜色
function pixelToColor(values) {
    const ndvi = values[0];
    if (ndvi === null || isNaN(ndvi)) return null;
    if (ndvi < 0.0) return "#636363";
    if (ndvi < 0.1) return "#d73027";
    if (ndvi < 0.2) return "#f46d43";
    if (ndvi < 0.3) return "#fdae61";
    if (ndvi < 0.4) return "#fee08b";
    if (ndvi < 0.5) return "#d9ef8b";
    if (ndvi < 0.6) return "#a6d96a";
    if (ndvi < 0.8) return "#1a9850";
    return "#006837";
}


/**
 * 初始化地图与绘图控件
 */
function initMap() {
    const imgLayer = L.tileLayer("http://t0.tianditu.gov.cn/img_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=19fc987939ebbcbcb3f0954ab6cf75be", {
        attribution: "天地图影像"
    });
    const vecLayer = L.tileLayer("http://t0.tianditu.gov.cn/vec_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=19fc987939ebbcbcb3f0954ab6cf75be", {
        attribution: "天地图矢量"
    });
    const labelLayer = L.tileLayer("http://t0.tianditu.gov.cn/cia_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=cia&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=19fc987939ebbcbcb3f0954ab6cf75be", {
        attribution: "注记"
    });

    map = L.map("map", {
        center: [39.065, 117.105],
        zoom: 16,
        layers: [imgLayer, labelLayer]
    });

    getCurrentLocation()
        .then(coords => map.setView([coords.latitude, coords.longitude], 16))
        .catch(err => console.warn("定位失败，使用默认坐标", err));

    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    const baseMaps = {
        "天地图影像": imgLayer,
        "天地图矢量": vecLayer
    };
    const overlayMaps = {
        "注记": labelLayer
    };

    const layersControl = L.control.layers(baseMaps, overlayMaps).addTo(map);

    window.drawControl = new L.Control.Draw({
        draw: {
            polygon: true,
            rectangle: false,
            marker: false,
            circle: false,
            circlemarker: false
        }
    });
    map.addControl(window.drawControl);

    map.on(L.Draw.Event.CREATED, async event => {
        const layer = event.layer;
        drawnItems.addLayer(layer);

        const shapeType = event.layerType;
        let coordinates;
        let area = 0;
        let centerForGeocode = null;

        if (shapeType === "circle") {
            const center = layer.getLatLng();
            const radius = layer.getRadius();
            coordinates = JSON.stringify({ shapeType, center, radius });
            area = Math.PI * radius * radius;
            centerForGeocode = [center.lng, center.lat];
        } else if (shapeType === "polygon") {
            const latlngs = layer.getLatLngs()[0];
            coordinates = JSON.stringify({ shapeType, latlngs });

            area = L.GeometryUtil.geodesicArea(latlngs);

            const coordsForTurf = latlngs.map(p => [p.lng, p.lat]);
            if (coordsForTurf.length > 0 &&
                (coordsForTurf[0][0] !== coordsForTurf[coordsForTurf.length - 1][0] ||
                    coordsForTurf[0][1] !== coordsForTurf[coordsForTurf.length - 1][1])) {
                coordsForTurf.push(coordsForTurf[0]);
            }
            const centroid = turf.centroid(turf.polygon([coordsForTurf]));
            centerForGeocode = centroid.geometry.coordinates;
        } else {
            alert("不支持该图形类型！");
            return;
        }

        area = (area / 666.67).toFixed(2); // 转亩

        let address = "未知位置";
        if (centerForGeocode) {
            try {
                const res = await fetch(`https://restapi.amap.com/v3/geocode/regeo?location=${centerForGeocode[0]},${centerForGeocode[1]}&key=9c7f97e95b93948af40ddab4871ffa18`);
                const data = await res.json();
                if (data.regeocode?.formatted_address) {
                    address = data.regeocode.formatted_address;
                }
            } catch (err) {
                console.warn("逆地理编码失败", err);
            }
        }

        layui.use('layer', function () {
            const layer = layui.layer;
            const url = `plot-admin-add.html?area=${area}`;
            const index = layer.open({
                type: 2,
                title: '新增地块',
                shadeClose: true,
                shade: 0.3,
                area: ['667px', '543px'],
                content: url
            });

            window.addEventListener("message", async event => {
                if (event.data.type === "submitPlot") {
                    const plotData = event.data.payload;
                    plotData.shapeType = shapeType;
                    plotData.coordinates = coordinates;
                    plotData.area = area;
                    plotData.address = address;

                    try {
                        const res = await fetch("http://localhost:8080/plots", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify(plotData)
                        });

                        if (!res.ok) throw new Error("请求失败");

                        const saved = await res.json();
                        console.log("发送到后端的数据:", plotData);

                        layer.close(index);
                        alert("保存成功！");
                        displayPlot(saved);

                    } catch (err) {
                        console.error("保存失败：", err);
                        alert("保存失败，请检查后端服务是否可用！");
                    }
                }
            }, { once: true });
        });
    });

    map.whenReady(() => {
        loadAndRenderPlots(layersControl, baseMaps, overlayMaps);
    });
}

/**
 * 加载地块数据并渲染，包括热力图
 * 传入图层控制器和图层对象，方便动态添加
 */
async function loadAndRenderPlots(layersControl, baseMaps, overlayMaps) {
    try {
        // 1. 检查地图容器是否准备就绪
        const mapContainer = document.getElementById('map');
        if (mapContainer.offsetWidth === 0 || mapContainer.offsetHeight === 0) {
            console.warn('地图容器不可见，延迟加载');
            setTimeout(() => loadAndRenderPlots(layersControl, baseMaps, overlayMaps), 100);
            return;
        }

        // 2. 获取真实地块数据
        let plots;
        try {
            const res = await fetch("http://localhost:8080/plots");
            if (!res.ok) throw new Error(`HTTP状态 ${res.status}`);
            plots = await res.json();
            console.log("✅ 从API获取地块数据：", plots);
        } catch (apiError) {
            alert("警告：API请求错误，真实数据加载失败");
        }

        // 3. 渲染地块并计算地图范围
        const featureGroup = L.featureGroup();
        plots.forEach(plot => {
            const layer = displayPlot(plot);
            if (layer) featureGroup.addLayer(layer);
        });

        // 自动调整地图视野（包含所有地块+10%边距）
        if (plots.length > 0) {
            map.fitBounds(featureGroup.getBounds().pad(0.1));
        }

        // 4. 生成增强版热力图数据
        const heatPoints = plots.flatMap((plot, index) => {
            try {
                if (!plot.coordinates) {
                    console.warn(`第${index}个地块缺少coordinates字段`);
                    return [];
                }

                const coord = JSON.parse(plot.coordinates);

                // 圆形地块处理
                if (coord.shapeType === "circle" && coord.center) {
                    return [
                        [coord.center.lat, coord.center.lng, 1.0], // 中心点
                        [coord.center.lat + 0.0002, coord.center.lng, 0.6], // 周边点
                        [coord.center.lat - 0.0002, coord.center.lng, 0.6]
                    ];
                }
                // 多边形地块处理
                else if (coord.shapeType === "polygon" && Array.isArray(coord.latlngs)) {
                    const bounds = L.latLngBounds(coord.latlngs);
                    return [
                        [bounds.getCenter().lat, bounds.getCenter().lng, 1.0], // 中心点
                        [bounds.getSouthWest().lat, bounds.getSouthWest().lng, 0.6], // 边界点
                        [bounds.getNorthEast().lat, bounds.getNorthEast().lng, 0.6]
                    ];
                }
                return [];
            } catch (err) {
                console.error(`处理第${index}个地块失败:`, err);
                return [];
            }
        }).filter(point =>
            point &&
            !isNaN(point[0]) &&
            !isNaN(point[1])
        );

        console.log("生成的热力点数据:", heatPoints);

        // 5. 安全创建热力图
        if (heatLayer) {
            map.removeLayer(heatLayer);  //
            if (layersControl && overlayMaps["热力图"]) {
                layersControl.removeLayer(overlayMaps["热力图"]);
            }
            delete overlayMaps["热力图"];
        }

        if (heatPoints.length > 0 && typeof L.heatLayer === "function") {
            heatLayer = L.heatLayer(heatPoints, {
                radius: 28,    // 控制热力点影响范围（像素）
                blur: 15,      // 控制模糊程度（越大越柔和）
                maxZoom: 18,   // 热力图最大显示级别
                minOpacity: 0.1, // 最小透明度（避免颜色太淡）
                gradient: {           // 自定义颜色渐变
                    0.4: 'blue',
                    0.6: 'cyan',
                    0.7: 'lime',
                    0.8: 'yellow',
                    1.0: 'red'
                }
            }).addTo(map);

            overlayMaps["热力图"] = heatLayer;

            // 添加热力图影像图层切换按钮
            if (layersControl) {
                layersControl.addOverlay(heatLayer, "热力图");
            }
        }

    } catch (err) {
        console.error("地块加载失败：", err);
        alert("地图加载错误: " + err.message);
    }
}


/**
 * 获取当前定位
 * @returns {Promise<unknown>}
 */
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('浏览器不支持定位'));
            return;
        }
        navigator.geolocation.getCurrentPosition(
            (pos) => resolve(pos.coords),
            (err) => reject(err),
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0,
            }
        );
    });
}


/**
 * 加载并渲染后端地块
 */
async function loadPlots() {
    try {
        const res = await fetch("http://localhost:8080/plots");
        if (!res.ok) throw new Error("请求失败");
        const plots = await res.json();
        plots.forEach(displayPlot);
    } catch (err) {
        console.error("地块加载失败：", err);
        alert("加载失败，请检查服务是否运行");
    }
}

/**
 * 渲染单个地块
 */
function displayPlot(plot) {
    const data = JSON.parse(plot.coordinates);
    let layer;

    if (data.shapeType === "circle") {
        layer = L.circle(data.center, {radius: data.radius});
    } else if (data.shapeType === "polygon") {
        layer = L.polygon(data.latlngs);
    } else {
        console.warn("未知形状类型", data.shapeType);
        return;
    }

    layer.addTo(map).bindPopup(`
        <b>地块名称:</b> ${plot.name}<br>
        <b>上季作物:</b> ${plot.lastCrop}<br>
        <b>本季作物:</b> ${plot.currentCrop}<br>
        <b>联系人:</b> ${plot.contactPerson}<br>
        <b>联系电话:</b> ${plot.phone}<br>
        <b>土壤类型:</b> ${plot.soilType}<br>
        <b>灌溉条件:</b> ${plot.irrigationType}<br>
        <b>土地类型:</b> ${plot.landType}<br>
        <b>面积:</b> ${plot.area} 亩<br>
        <button onclick="updateArea(${plot.id})">修改面积</button>
        <button onclick="deletePlot(${plot.id})">删除</button>
    `);

    return layer;
}

/**
 * 删除地块
 */
async function deletePlot(id) {
    if (!confirm("确认删除该地块？")) return;

    try {
        const res = await fetch(`http://localhost:8080/plots/${id}`, {
            method: "DELETE"
        });

        if (!res.ok) throw new Error("删除失败");

        alert("删除成功，请刷新页面查看...");
        loadPlots(); // 重新加载地块数据，刷新地图展示

    } catch (err) {
        console.error(err);
        alert("删除失败，请检查后端接口或网络状态");
    }
}



/**
 * 搜索地址并跳转地图位置
 */
function setupSearch() {
    const btn = document.getElementById("searchBtn");
    const input = document.getElementById("searchInput");

    const doSearch = async () => {
        const keyword = input.value.trim();
        if (!keyword) {
            layer.msg("请输入关键字", {icon: 0});
            return;
        }

        const url = `https://api.tianditu.gov.cn/geocoder?ds={"keyWord":"${keyword}"}&tk=19fc987939ebbcbcb3f0954ab6cf75be`;

        try {
            const res = await fetch(url);
            const data = await res.json();
            if (data?.location) {
                const {lon, lat} = data.location;
                const latlng = [lat, lon];
                map.setView(latlng, 14);
                L.marker(latlng).addTo(map).bindPopup(`搜索结果：${keyword}`).openPopup();
                layer.msg("定位成功", {icon: 1});
            } else {
                layer.alert("未找到该位置", {icon: 2});
            }
        } catch (err) {
            console.error("搜索失败：", err);
            layer.alert("搜索失败，请检查网络或天地图服务", {icon: 2});
        }
    };

    btn.addEventListener("click", doSearch);
    input.addEventListener("keypress", e => {
        if (e.key === "Enter") doSearch();
    });
}


/**
 * 修改面积（亩）
 */
async function updateArea(id) {
    const input = prompt("请输入新的面积（亩）：");
    if (input === null || input.trim() === "") {
        alert("面积不能为空");
        return;
    }

    const area = parseFloat(input.trim());

    if (isNaN(area) || area <= 0) {
        alert("请输入大于0的数字");
        return;
    }

    try {
        const res = await fetch(`http://localhost:8080/plots/${id}/area`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ area: parseFloat(area.toFixed(2)) }) // 保留两位小数
        });

        if (!res.ok) throw new Error("更新失败");
        alert("更新成功");
        loadPlots();
    } catch (err) {
        console.error("更新失败：", err);
        alert("更新失败，请检查后端服务");
    }
}


// 全屏地图绘制
const drawControls = document.getElementById('drawControls');
drawControls.style.display = 'none';

const startDrawBtn = document.getElementById('startDrawBtn');
let currentDrawer = null;
let drawingFinished = false;

// 退出全屏清理逻辑封装
function handleExitFullscreenCleanup() {
    console.log('退出全屏，清理绘图状态...');
    drawControls.style.display = 'none';
    if (currentDrawer) {
        currentDrawer.disable();
        currentDrawer = null;
    }

    // 如果是绘制完成后退出全屏，显示填写弹窗
    if (drawingFinished) {
        setTimeout(() => {
            drawingFinished = false; // 重置状态
        }, 100);
    }
}

// 监听全屏变化（退出时清理）
document.addEventListener("fullscreenchange", () => {
    if (!document.fullscreenElement) {
        handleExitFullscreenCleanup();
    }
});

// 进入全屏并初始化地图状态（不自动绘图）
async function enterDrawMode() {
    const mapContainer = document.getElementById("map");
    console.log('请求进入全屏...');

    try {
        if (mapContainer.requestFullscreen) {
            await mapContainer.requestFullscreen();
        } else if (mapContainer.webkitRequestFullscreen) {
            await mapContainer.webkitRequestFullscreen();
        } else if (mapContainer.msRequestFullscreen) {
            await mapContainer.msRequestFullscreen();
        }
        console.log('进入全屏成功！');

        setTimeout(async () => {
            console.log('刷新地图和显示按钮');
            map.invalidateSize();
            map.setZoom(17);

            try {
                // 替换原来的定位代码
                const currentCenter = map.getCenter();
                const currentZoom = map.getZoom();

                if (currentZoom < 17) {
                    map.setView(currentCenter, 17);
                } else {
                    map.setView(currentCenter, currentZoom);
                }
            } catch (err) {
                console.warn('定位失败，使用默认坐标', err);
                map.setView([39.065, 117.105]);
            }

            // 显示绘图控制按钮和提示文字
            drawControls.style.display = 'flex';
            showCustomMsg("已进入圈地模式，请点击“开始绘制”按钮");

            console.log('按钮和提示显示了！');

        }, 300);

    } catch (err) {
        console.error('全屏失败:', err);
    }
}

// 点击“开始圈地”按钮（进入全屏并启动绘图）
startDrawBtn.addEventListener('click', async (e) => {
    e.stopPropagation();
    if (currentDrawer) {
        currentDrawer.disable();
        currentDrawer = null;
    }
    await enterDrawMode();
});

// 点击“开始绘图”按钮：启用绘图工具
document.getElementById('btn-start').addEventListener('click', (e) => {
    e.stopPropagation();
    if (currentDrawer) {
        currentDrawer.disable();
        currentDrawer = null;
    }

    if (window.drawControl) {
        currentDrawer = new L.Draw.Polygon(map, window.drawControl.options.draw.polygon);

        // 监听绘制完成事件
        map.on('draw:created', function(e) {
            const layer = e.layer;
            // 可以在这里处理绘制好的多边形数据
            console.log('绘制完成:', layer.toGeoJSON());

            // 标记绘制已完成
            drawingFinished = true;

            // 退出全屏
            if (document.fullscreenElement) {
                document.exitFullscreen();
            }
        });

        currentDrawer.enable();
    } else {
        layer.msg("绘图控件未初始化", {icon: 2});
    }
});

// 完成绘图
document.getElementById('btn-finish').addEventListener('click', (e) => {
    e.stopPropagation();
    if (currentDrawer) {
        // 使用公开API触发绘制完成事件，而不是调用私有方法
        currentDrawer._fireCreated();
        currentDrawer.disable();
        currentDrawer = null;
    }
});

// 撤销最后一个点
function undoLastVertex(e) {
    e.preventDefault();
    e.stopPropagation();
    if (currentDrawer && currentDrawer.enabled() && currentDrawer.deleteLastVertex) {
        currentDrawer.deleteLastVertex();
    } else {
        layer.msg("当前没有正在绘制的多边形，无法撤回", {icon: 0, time: 2000});
    }
}

const undoBtn = document.getElementById('btn-undo');
undoBtn.addEventListener('click', undoLastVertex);
undoBtn.addEventListener('touchstart', undoLastVertex); // 手机兼容

// 取消绘图
document.getElementById('btn-cancel').addEventListener('click', (e) => {
    e.stopPropagation();
    drawingFinished = false; // 重置状态
    if (currentDrawer) {
        currentDrawer.disable();
        currentDrawer = null;
    }
    drawControls.style.display = 'none';
    if (document.fullscreenElement) {
        document.exitFullscreen();
    }
});


// 这里是单纯全屏展示的功能
document.getElementById("btnFullscreenOnly").addEventListener("click", async () => {
    const mapContainer = document.getElementById("map");
    console.log('请求进入纯浏览全屏模式...');

    try {
        if (mapContainer.requestFullscreen) {
            await mapContainer.requestFullscreen();
        } else if (mapContainer.webkitRequestFullscreen) {
            await mapContainer.webkitRequestFullscreen();
        } else if (mapContainer.msRequestFullscreen) {
            await mapContainer.msRequestFullscreen();
        }

        setTimeout(() => {
            map.invalidateSize();  // 重要：重绘地图以适配全屏尺寸
            console.log('✅ 已进入纯地图全屏模式');
        }, 300);

    } catch (err) {
        console.error("❌ 无法进入全屏：", err);
        alert("浏览器不支持或用户取消了全屏操作");
    }
});
//自动退出全屏时恢复地图尺寸
document.addEventListener("fullscreenchange", () => {
    if (!document.fullscreenElement) {
        console.log("🧭 退出了全屏模式");
        setTimeout(() => {
            map.invalidateSize();  // 退出全屏后也要刷新地图
        }, 300);
    }
});


// 显示提示信息
function showCustomMsg(text, duration = 3000) {
    const tip = document.getElementById('drawTip');
    if (!tip) return;
    tip.innerText = text;
    tip.style.display = 'block';
    tip.style.opacity = '0';
    setTimeout(() => {
        tip.style.opacity = '1';
    }, 10);
    setTimeout(() => {
        tip.style.opacity = '0';
        setTimeout(() => {
            tip.style.display = 'none';
        }, 300);
    }, duration);
}


// 查询地块功能（layui）
layui.use(['layer', 'laytpl'], function () {
    const layer = layui.layer;
    const laytpl = layui.laytpl;

    document.getElementById('queryPlot').onclick = async function () {
        try {
            const res = await fetch("http://localhost:8080/plots");
            if (!res.ok) throw new Error("获取地块数据失败");
            const plots = await res.json();

            const tpl = `
              <style>
                #plotSearchInput {
                    flex: 1;
                    padding: 8px 12px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    font-size: 14px;
                }
                #plotList {
                    max-height: 320px;
                    overflow-y: auto;
                    list-style: none;
                    padding: 0;
                    margin: 0;
                }
                #plotList li {
                    background: #f8f8f8;
                    padding: 12px 16px;
                    margin-bottom: 8px;
                    border-radius: 6px;
                    cursor: pointer;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    transition: background-color 0.2s ease;
                }
                #plotList li:hover {
                    background-color: #e6f7ff;
                }
              </style>
              <div style="padding: 16px; font-family: Arial, sans-serif;">
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                  <i class="layui-icon layui-icon-search" style="margin-right: 8px; font-size: 18px; color: #5FB878;"></i>
                  <input id="plotSearchInput" type="text" placeholder="请输入地块名称进行搜索" />
                </div>
                <ul id="plotList">
                  {{# layui.each(d.plots, function(index, item){ }}
                    <li data-index="{{ index }}">
                      <i class="layui-icon layui-icon-location" style="color: #1E9FFF; margin-right: 6px;"></i>
                      {{ item.name }}
                    </li>
                  {{# }); }}
                </ul>
              </div>
            `;

            laytpl(tpl).render({plots}, function (html) {
                layer.open({
                    type: 1,
                    title: '查询地块',
                    area: ['400px', '400px'],
                    content: html,
                    success: function () {
                        const input = document.getElementById('plotSearchInput');
                        const list = document.getElementById('plotList');

                        input.oninput = function () {
                            const keyword = this.value.toLowerCase();
                            list.querySelectorAll('li').forEach(li => {
                                const name = li.textContent.toLowerCase();
                                li.style.display = name.includes(keyword) ? 'block' : 'none';
                            });
                        };

                        list.querySelectorAll('li').forEach(li => {
                            li.onclick = function () {
                                const index = parseInt(this.getAttribute('data-index'));
                                const plot = plots[index];

                                const layerObj = displayPlot(plot);

                                if (layerObj.getBounds) {
                                    map.fitBounds(layerObj.getBounds());
                                } else if (layerObj.getLatLng) {
                                    map.setView(layerObj.getLatLng(), 16);
                                }

                                layerObj.openPopup();
                                layer.closeAll();
                            };
                        });
                    }
                });
            });
        } catch (err) {
            console.error(err);
            layer.msg("获取地块数据失败，请检查后端服务", {icon: 2});
        }
    };
});



