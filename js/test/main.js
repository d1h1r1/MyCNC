import * as fabric from 'fabric'; // v6

// 创建 Fabric.js Canvas 实例
const canvas = new fabric.Canvas('myCanvas');

// 加载 SVG 文件并解析
// fabric.loadSVGFromURL('phone.svg', function(objects, options) {
// 	// 将解析后的 SVG 对象合并为一个组
// 	const svgGroup = fabric.util.groupSVGElements(objects, options);

// 	// 将该组添加到 Canvas 上
// 	canvas.add(svgGroup);

// 	// 可选：调整大小
// 	svgGroup.scaleToWidth(300);
// 	svgGroup.scaleToHeight(300);

// 	// 重新渲染 Canvas
// 	canvas.renderAll();
// });

fabric.loadSVGFromString(svgString, function(objects, options) {
    const svgGroup = fabric.util.groupSVGElements(objects, options);
    canvas.add(svgGroup);
		// 可选：调整大小
		svgGroup.scaleToWidth(300);
		svgGroup.scaleToHeight(300);
	
		// 重新渲染 Canvas
		canvas.renderAll();
});