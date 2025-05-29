let map;            // 地图实例
let drawnItems;     // 用户绘制图层集合

// 页面加载完成初始化地图与功能
document.addEventListener("DOMContentLoaded", () => {
    initMap();
    loadPlots();
    setupSearch();
});

/**
 * 初始化地图与绘图控件
 */
function initMap() {
    // 添加天地图影像图层（底图1）
    const imgLayer = L.tileLayer("http://t0.tianditu.gov.cn/img_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=19fc987939ebbcbcb3f0954ab6cf75be", {
        attribution: "天地图影像"
    });
    // 添加天地图矢量图层（底图2）
    const vecLayer = L.tileLayer("http://t0.tianditu.gov.cn/vec_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=19fc987939ebbcbcb3f0954ab6cf75be", {
        attribution: "天地图矢量"
    });
    // 注记图层
    const labelLayer = L.tileLayer("http://t0.tianditu.gov.cn/cia_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=cia&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=19fc987939ebbcbcb3f0954ab6cf75be");


    // 地图初始化
    map = L.map("map", {
        center: [39.065, 117.1050], zoom: 16, layers: [imgLayer, labelLayer] // 默认显示图层：影像+注记
    });

    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);


    // 可切换的底图图层集合
    const baseMaps = {
        "天地图影像": imgLayer, "天地图矢量": vecLayer
    };
    // 可叠加图层集合（注记图层）
    const overlayMaps = {
        "注记": labelLayer
    };
    // 添加图层控制器到地图
    L.control.layers(baseMaps, overlayMaps).addTo(map);


    // 设置绘图控件（支持绘制多边形和圆）
    const drawControl = new L.Control.Draw({
        draw: {
            polygon: true, rectangle: false, marker: false, circle: true, circlemarker: false
        }
    });
    map.addControl(drawControl);

    // 监听绘图完成事件
    map.on(L.Draw.Event.CREATED, async (event) => {
        const layer = event.layer;
        drawnItems.addLayer(layer);

        const shapeType = event.layerType;
        let coordinates;
        let area = 0;

        if (shapeType === "circle") {
            const center = layer.getLatLng();
            const radius = layer.getRadius();
            coordinates = JSON.stringify({shapeType, center, radius});
            area = Math.PI * radius * radius;
        } else if (shapeType === "polygon") {
            const latlngs = layer.getLatLngs()[0]; // 获取顶点
            coordinates = JSON.stringify({shapeType, latlngs});

            // 使用 Leaflet.Draw 自带的面积计算函数（单位：平方米）
            area = L.GeometryUtil.geodesicArea(latlngs);
        }
        area = (area / 666.67).toFixed(2); // 面积转换为亩，并保留两位小数


        // 弹出地块添加页面并传递当前的面积数据
        const url = `plot-admin-add.html?area=${area}`;
        //使弹窗位于屏幕中间
        const width = 667;
        const height = 543;
        const left = (window.screen.width - width) / 2;
        const top = (window.screen.height - height) / 2;
        const popupWindow = window.open(url, '_blank', `width=${width},height=${height},left=${left},top=${top}`);

        // 在弹出的页面中获取用户输入的数据
        popupWindow.onload = () => {
            const form = popupWindow.document.querySelector('#plotForm');
            form.onsubmit = async (e) => {
                e.preventDefault();

                // 获取输入的数据
                const name = form.querySelector('[name="name"]').value;
                const lastCrop = form.querySelector('[name="lastCrop"]').value;
                const currentCrop = form.querySelector('[name="currentCrop"]').value;
                const contactPerson = form.querySelector('[name="contactPerson"]').value;
                const phone = form.querySelector('[name="phone"]').value;
                const soilType = form.querySelector('[name="soilType"]').value;
                const irrigationType = form.querySelector('[name="irrigation"]').value;
                const landType = form.querySelector('[name="landType"]').value;


                // 校验输入
                if (!name || !/^[\u4e00-\u9fa5a-zA-Z0-9]+$/.test(name) || name.length > 20) {
                    alert("地块名称无效！");
                    return;
                }

                if (!lastCrop || !currentCrop) {
                    alert("请填写作物信息！");
                    return;
                }

                if (!contactPerson || !phone) {
                    alert("请填写联系人和电话！");
                    return;
                }

                if (!soilType) {
                    alert("请选择土壤类型！");
                    return;
                }

                // 封装地块信息
                const plotData = {
                    name,
                    lastCrop,
                    currentCrop,
                    contactPerson,
                    phone,
                    soilType,
                    irrigationType,
                    landType,
                    shapeType,
                    coordinates,
                    area
                };

                try {
                    const res = await fetch("http://localhost:8080/plots", {
                        method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(plotData)
                    });
                    if (!res.ok) throw new Error("请求失败");

                    const saved = await res.json();
                    popupWindow.close(); // 关闭弹窗
                    alert("保存成功！");
                    displayPlot(saved); // 显示地块
                } catch (err) {
                    console.error("保存失败：", err);
                    alert("保存失败，请检查后端服务是否可用！");
                }
            };
        };
    }); // map.on(L.Draw.Event.CREATED)


}

/**
 * 加载并渲染后端已保存的地块数据
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
 * 渲染单个地块图层，并绑定弹窗信息
 */
function displayPlot(plot) {
    const data = JSON.parse(plot.coordinates);
    let layer;

    if (data.shapeType === "circle") {
        layer = L.circle(data.center, {radius: data.radius});
    } else {
        layer = L.polygon(data.latlngs);
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
 * 删除指定地块
 */
async function deletePlot(id) {
    if (!confirm("确认删除该地块？")) return;

    try {
        const res = await fetch(`http://localhost:8080/plots/${id}`, {method: "DELETE"});
        if (!res.ok) throw new Error("删除失败");
        alert("删除成功，请刷新页面查看");
    } catch (err) {
        console.error("删除失败：", err);
        alert("删除失败，请检查后端接口");
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


// 更新面积按钮事件
async function updateArea(id) {
    const newArea = prompt("请输入新的面积（亩）：");

    if (newArea === null || newArea.trim() === "") {
        alert("面积不能为空");
        return;
    }

    const area = parseFloat(newArea.trim()).toFixed(2); // 保留两位小数

    // 验证面积格式
    if (isNaN(area) || area <= 0) {
        alert("面积必须大于0并且是数字");
        return;
    }

    try {
        const res = await fetch(`http://localhost:8080/plots/${id}/area`, {
            method: "PUT", headers: {
                "Content-Type": "application/json",
            }, body: JSON.stringify(area)
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


//  查询地块
layui.use(['layer', 'laytpl'], function () {
    const layer = layui.layer;
    const laytpl = layui.laytpl;

    document.getElementById('queryPlot').onclick = async function () {
        try {
            const res = await fetch("http://localhost:8080/plots");
            if (!res.ok) throw new Error("获取地块数据失败");
            const plots = await res.json();

            const tpl = `
              <div style="padding: 16px; font-family: Arial, sans-serif;">
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                  <i class="layui-icon layui-icon-search" style="margin-right: 8px; font-size: 18px; color: #5FB878;"></i>
                  <input 
                    id="plotSearchInput" 
                    type="text" 
                    placeholder="请输入地块名称进行搜索" 
                    style="flex: 1; padding: 8px 12px; border: 1px solid #ccc; border-radius: 4px;" 
                  />
                </div>
                <ul 
                  id="plotList" 
                  style="
                    max-height: 320px; 
                    overflow-y: auto; 
                    list-style: none; 
                    padding: 0; 
                    margin: 0;
                  "
                >
                  {{# layui.each(d.plots, function(index, item){ }}
                    <li 
                      data-index="{{ index }}" 
                      style="
                        background: #f8f8f8; 
                        padding: 12px 16px; 
                        margin-bottom: 8px; 
                        border-radius: 6px; 
                        cursor: pointer; 
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
                        transition: all 0.2s ease;
                      "
                      onmouseover="this.style.backgroundColor='#e6f7ff'" 
                      onmouseout="this.style.backgroundColor='#f8f8f8'"
                    >
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
                        document.getElementById('plotSearchInput').oninput = function () {
                            const keyword = this.value.toLowerCase();
                            const list = document.getElementById('plotList');
                            list.querySelectorAll('li').forEach(li => {
                                const name = li.textContent.toLowerCase();
                                li.style.display = name.includes(keyword) ? 'block' : 'none';
                            });
                        };

                        document.querySelectorAll('#plotList li').forEach(li => {
                            li.onclick = function () {
                                const index = parseInt(this.getAttribute('data-index'));
                                const plot = plots[index];

                                const layerObj = displayPlot(plot);

                                // 自动定位并弹窗
                                if (layerObj.getBounds) {
                                    map.fitBounds(layerObj.getBounds());
                                } else if (layerObj.getLatLng) {
                                    map.setView(layerObj.getLatLng(), 16);
                                }

                                layerObj.openPopup(); // 弹出地块信息
                                layer.closeAll();     // 关闭查询弹窗
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

