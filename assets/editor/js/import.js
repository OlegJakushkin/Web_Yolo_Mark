// functions related to importing

pg.import = function () {

    var importAndAddExternalImage = function (url, callback) {
        var xhr = new XMLHttpRequest();
        xhr.onload = function () {
            var reader = new FileReader();
            reader.onloadend = function () {
                importAndAddImage(reader.result);
            };
            reader.readAsDataURL(xhr.response);
        };
        xhr.open('GET', url);
        xhr.responseType = 'blob';
        xhr.send();
    };


    var importAndAddImage = function (src) {

        var l = pg.layer.getActiveLayer().id;

        var backgrowndLayer = pg.layer.addNewLayer('Image layer');
        backgrowndLayer.data.isDefaultLayer = false;
        backgrowndLayer.data.id = 666;
        pg.layer.ensureGuideLayer();
        backgrowndLayer.activate();
        pg.layerPanel.updateLayerList();

        d = new paper.Raster({
            source: src,
            position: new paper.Point(0, 0)
        });
        d.onLoad = function () {
            h = paper.view.bounds.height / d.height
            w = paper.view.bounds.width / d.width
            s = Math.min(h, w)

            if (s < 1) {
                pg.view.zoomBy(s)
            }
            d.data.noSelect = true;
            backgrowndLayer.sendToBack();

            pg.layer.activateDefaultLayer()
            pg.undo.snapshot('importImage');


        }
    };


    var importAndAddSVG = function (svgString) {
        paper.project.importSVG(svgString, {expandShapes: true});
        pg.undo.snapshot('importAndAddSVG');
        paper.project.view.update();
    };


    return {
        importAndAddImage: importAndAddImage,
        importAndAddExternalImage: importAndAddExternalImage,
        importAndAddSVG: importAndAddSVG
    };
}();