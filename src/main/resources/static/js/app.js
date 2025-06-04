let map;            // 地图实例
let drawnItems;     // 用户绘制图层集合

document.addEventListener("DOMContentLoaded", () => {
    initMap();
    loadPlots();
    setupSearch();
});


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

    // 默认中心为天津工业大学，获得到定位后覆盖
    map = L.map("map", {
        center: [39.065, 117.105],
        zoom: 16,
        layers: [imgLayer, labelLayer]
    });

    // 尝试获取当前定位，成功后调整中心
    getCurrentLocation()
        .then(coords => {
            map.setView([coords.latitude, coords.longitude], 16);
        })
        .catch(err => {
            console.warn('定位失败，使用默认坐标', err);
        });


    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    const baseMaps = {
        "天地图影像": imgLayer,
        "天地图矢量": vecLayer
    };
    const overlayMaps = {
        "注记": labelLayer
    };
    L.control.layers(baseMaps, overlayMaps).addTo(map);

    window.drawControl = new L.Control.Draw({
        draw: {
            polygon: true,
            rectangle: false,
            marker: false,
            circle: false,       // 你代码里用了circle，必须开启
            circlemarker: false
        }
    });
    map.addControl(window.drawControl);

    map.on(L.Draw.Event.CREATED, async (event) => {
        const layer = event.layer;
        drawnItems.addLayer(layer);

        const shapeType = event.layerType;
        let coordinates;
        let area = 0;
        let centerForGeocode = null;

        if (shapeType === "circle") {
            const center = layer.getLatLng();
            const radius = layer.getRadius();
            coordinates = JSON.stringify({shapeType, center, radius});
            area = Math.PI * radius * radius;
            centerForGeocode = [center.lng, center.lat];
        } else if (shapeType === "polygon") {
            const latlngs = layer.getLatLngs()[0];
            coordinates = JSON.stringify({shapeType, latlngs});

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

        const url = `plot-admin-add.html?area=${area}`;  // 不传地址，前端填写
        const width = 667, height = 543;
        const left = (window.screen.width - width) / 2;
        const top = (window.screen.height - height) / 2;
        const popupWindow = window.open(url, '_blank', `width=${width},height=${height},left=${left},top=${top}`);

        // 通过postMessage通信更安全，不推荐直接操作popup DOM（跨域等坑）
        window.addEventListener("message", async (event) => {
            if (event.source === popupWindow && event.data.type === "submitPlot") {
                const plotData = event.data.payload;
                // 补充shapeType、coordinates、area、address
                plotData.shapeType = shapeType;
                plotData.coordinates = coordinates;
                plotData.area = area;
                plotData.address = address;

                try {
                    const res = await fetch("http://localhost:8080/plots", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify(plotData)
                    });
                    if (!res.ok) throw new Error("请求失败");
                    const saved = await res.json();
                    popupWindow.close();
                    alert("保存成功！");
                    displayPlot(saved);
                } catch (err) {
                    console.error("保存失败：", err);
                    alert("保存失败，请检查后端服务是否可用！");
                }
            }
        }, {once: true});
    });
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
        const res = await fetch(`http://localhost:8080/plots/${id}`, {method: "DELETE"});
        if (!res.ok) throw new Error("删除失败");
        alert("删除成功，请刷新页面查看");
        loadPlots();
    } catch (err) {
        console.error(err);
        alert("删除失败");
    }
}

/**
 * 修改面积示例
 */
async function updateArea(id) {
    const newArea = prompt("请输入新的面积（亩）");
    if (!newArea) return;

    try {
        const res = await fetch(`http://localhost:8080/plots/${id}/area`, {
            method: "PUT",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({area: newArea})
        });
        if (!res.ok) throw new Error("更新失败");
        alert("更新成功");
        loadPlots();
    } catch (err) {
        console.error(err);
        alert("更新失败");
    }
}

/**
 * 简单搜索功能示范（天地图POI检索接口）
 */
function setupSearch() {
    const searchBtn = document.getElementById("searchBtn");
    const searchInput = document.getElementById("searchInput");

    searchBtn.onclick = async () => {
        const keyword = searchInput.value.trim();
        if (!keyword) return alert("请输入搜索关键词");

        try {
            const res = await fetch(`http://api.tianditu.gov.cn/search?postStr={"keyWord":"${keyword}","level":"15","mapBound":"39.4,116.8,38.8,117.5","queryType":"1"}&type=search&tk=19fc987939ebbcbcb3f0954ab6cf75be`);
            if (!res.ok) throw new Error("搜索失败");
            const data = await res.json();

            if (data.datas && data.datas.length > 0) {
                const first = data.datas[0];
                map.setView([first.y, first.x], 17);
                L.popup().setLatLng([first.y, first.x]).setContent(`<b>${first.name}</b><br>${first.address}`).openOn(map);
            } else {
                alert("无搜索结果");
            }
        } catch (err) {
            console.error(err);
            alert("搜索异常");
        }
    };
}

// 更新面积按钮事件
async function updateArea(id) {
    const newArea = prompt("请输入新的面积（亩）：");

    if (newArea === null || newArea.trim() === "") {
        alert("面积不能为空");
        return;
    }

    const area = parseFloat(newArea.trim());

    // 验证面积格式
    if (isNaN(area) || area <= 0) {
        alert("面积必须大于0并且是数字");
        return;
    }

    try {
        const res = await fetch(`http://localhost:8080/plots/${id}/area`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({area}), // 传对象更语义化
        });

        if (!res.ok) {
            alert("更新失败，请检查后端服务");
            return;
        }

        const updatedPlot = await res.json();
        alert("面积更新成功！");
        loadPlots(); // 重新加载地块数据

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

// 退出全屏清理逻辑封装
function handleExitFullscreenCleanup() {
    console.log('退出全屏，清理绘图状态...');
    drawControls.style.display = 'none';
    if (currentDrawer) {
        currentDrawer.disable();
        currentDrawer = null;
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
                const coords = await getCurrentLocation();
                map.setView([coords.latitude, coords.longitude]);
                console.log('定位成功，已设置视图', coords);
            } catch (err) {
                console.warn('定位失败，使用默认坐标', err);
                map.setView([39.065, 117.105]);
            }

            // 显示绘图控制按钮和提示文字
            drawControls.style.display = 'flex';
            showCustomMsg("已进入圈地模式，请点击“开始绘图”按钮");

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
        currentDrawer.enable();
    } else {
        layer.msg("绘图控件未初始化", { icon: 2 });
    }
});

// 完成绘图
document.getElementById('btn-finish').addEventListener('click', (e) => {
    e.stopPropagation();
    if (currentDrawer) {
        currentDrawer._fireCreated();
        currentDrawer.disable();
        currentDrawer = null;
    }
    drawControls.style.display = 'none';
    if (document.fullscreenElement) {
        document.exitFullscreen();
    }
});

// 撤销最后一个点
function undoLastVertex(e) {
    e.preventDefault();
    e.stopPropagation();
    if (currentDrawer && currentDrawer.enabled() && currentDrawer.deleteLastVertex) {
        currentDrawer.deleteLastVertex();
    } else {
        layer.msg("当前没有正在绘制的多边形，无法撤回", { icon: 0, time: 2000 });
    }
}
const undoBtn = document.getElementById('btn-undo');
undoBtn.addEventListener('click', undoLastVertex);
undoBtn.addEventListener('touchstart', undoLastVertex); // 手机兼容

// 取消绘图
document.getElementById('btn-cancel').addEventListener('click', (e) => {
    e.stopPropagation();
    if (currentDrawer) {
        currentDrawer.disable();
        currentDrawer = null;
    }
    drawControls.style.display = 'none';
    if (document.fullscreenElement) {
        document.exitFullscreen();
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
