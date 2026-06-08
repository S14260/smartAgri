// 全局变量
let map;               // 地图实例
let drawnItems;        // 用户绘制图层集合
let currentNdviTime = null;






function initMap() {


    // AI 自动圈地按钮
    const btn = document.getElementById("btnAiDraw");
    btn.onclick = async function () {
        drawnItems.clearLayers();
        allPolygons.forEach(p => map.removeLayer(p));

        // 截图当前地图
        leafletImage(map, async function (err, canvas) {
            if (err) { alert("截图失败"); return; }

            canvas.toBlob(async function (blob) {
                const bounds = map.getBounds();
                const payload = new FormData();
                payload.append("file", blob, "screenshot.jpg");
                payload.append("bounds", JSON.stringify([
                    [bounds.getNorth(), bounds.getWest()],
                    [bounds.getSouth(), bounds.getEast()]
                ]));

                try {
                    const res = await fetch("http://123.56.228.32:8001/predict", { method: "POST", body: payload });
                    if (!res.ok) throw new Error(`HTTP ${res.status}`);
                    const data = await res.json();

                    if (data.polygons) {
                        // 调用简化接口
                        const simplifyRes = await fetch("http://123.56.228.32:8010/simplify", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ polygons: data.polygons, tolerance: simplifyRange.value / 100000 })
                        });
                        const simpleData = await simplifyRes.json();
                        allPolygons = [];

                        simpleData.simplified_polygons.forEach(latlngs => {
                            const poly = L.polygon(latlngs, { color: "red", fillOpacity: 0.15 });
                            allPolygons.push(poly);
                            poly.addTo(map);
                        });

                        alert("✅ 点击任意地块中间选择该地块！");
                    } else if (data.error) {
                        alert("AI预测出错: " + data.error);
                    }
                } catch (err) {
                    alert("请求失败: " + err.message);
                }
            }, "image/jpeg", 0.7);
        });
    };

    // 点击地图选择单个地块
    map.on("click", function (e) {
        if (allPolygons.length === 0) return;

        const clickedPoint = e.latlng;
        let selectedPolygon = null;

        for (const poly of allPolygons) {
            const latlngs = poly.getLatLngs()[0];
            if (isPointInPolygon(clickedPoint, latlngs)) {
                selectedPolygon = poly;
                break;
            }
        }

        if (selectedPolygon) {
            drawnItems.clearLayers();
            allPolygons.forEach(p => map.removeLayer(p));
            selectedPolygon.setStyle({ color: "red", fillOpacity: 0.4 });
            drawnItems.addLayer(selectedPolygon);
            drawControl._toolbars.edit._modes.edit.handler.enable();
            openPlotForm(selectedPolygon);
        }
    });
}

/**
 * 射线法判断点是否在多边形内部
 */
function isPointInPolygon(point, vs) {
    const x = point.lng, y = point.lat;
    let inside = false;
    for (let i = 0, j = vs.length - 1; i < vs.length; j = i++) {
        const xi = vs[i].lng, yi = vs[i].lat;
        const xj = vs[j].lng, yj = vs[j].lat;
        const intersect = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
    }
    return inside;
}

/**
 * 弹出输入表单，保存地块到后端
 */
function openPlotForm(poly) {
    const area = (L.GeometryUtil.geodesicArea(poly.getLatLngs()[0]) / 666.67).toFixed(2);
    const url = `plot-admin-add.html?area=${area}`;
    const width = 667, height = 543;
    const left = (window.screen.width - width) / 2;
    const top = (window.screen.height - height) / 2;
    const popupWindow = window.open(url, "_blank", `width=${width},height=${height},left=${left},top=${top}`);

    popupWindow.onload = () => {
        const form = popupWindow.document.querySelector("#plotForm");
        form.onsubmit = async (e) => {
            e.preventDefault();
            const name = form.querySelector('[name="name"]').value;
            const lastCrop = form.querySelector('[name="lastCrop"]').value;
            const currentCrop = form.querySelector('[name="currentCrop"]').value;
            const contactPerson = form.querySelector('[name="contactPerson"]').value;
            const phone = form.querySelector('[name="phone"]').value;
            const soilType = form.querySelector('[name="soilType"]').value;
            const irrigationType = form.querySelector('[name="irrigation"]').value;
            const landType = form.querySelector('[name="landType"]').value;

            if (!name || !/^[\u4e00-\u9fa5a-zA-Z0-9]+$/.test(name) || name.length > 20) { alert("地块名称无效！"); return; }
            if (!lastCrop || !currentCrop) { alert("请填写作物信息！"); return; }
            if (!contactPerson || !phone) { alert("请填写联系人和电话！"); return; }
            if (!soilType) { alert("请选择土壤类型！"); return; }

            const latlngs = poly.getLatLngs()[0];
            const coordinates = JSON.stringify({ shapeType: "polygon", latlngs });
            const plotData = { name, lastCrop, currentCrop, contactPerson, phone, soilType, irrigationType, landType, shapeType: "polygon", coordinates, area };

            try {
                const res = await fetch("http://localhost:8080/plots", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(plotData) });
                if (!res.ok) throw new Error("请求失败");
                const saved = await res.json();
                popupWindow.close();
                alert("保存成功！");
                displayPlot(saved);
            } catch (err) {
                console.error(err);
                alert("保存失败，请检查后端服务");
            }
        };
    };
}






















