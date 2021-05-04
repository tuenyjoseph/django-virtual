  $(function () {
    $("#id_cover").change(function() {
      if (this.files && this.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
          $("#image").attr("src", e.target.result);
          $("#modalCrop").modal("show");
        }
        reader.readAsDataURL(this.files[0]);
      }
    });

    var $image = $("#image");
    var cropBoxData;
    var canvasData;
    $("#modalCrop").on("shown.bs.modal", function () {
      $image.cropper({
        viewMode: 1,
        aspectRatio:3/1,
        minCropBoxWidth: 900,
        minCropBoxHeight: 300,
        ready: function () {
          $image.cropper("setCanvasData", canvasData);
          $image.cropper("setCropBoxData", cropBoxData);
        }
      });
    }).on("hidden.bs.modal", function () {
      cropBoxData = $image.cropper("getCropBoxData");
      canvasData = $image.cropper("getCanvasData");
      $image.cropper("destroy");
    });
    $(".js-zoom-in").click(function () {
      $image.cropper("zoom", 0.1);
    });
    $(".js-zoom-out").click(function () {
      $image.cropper("zoom", -0.1);
    });

    $(".js-crop-and-upload").click(function () {
      var cropData = $image.cropper("getData");
      $("#id_x").val(cropData["x"]);
      $("#id_y").val(cropData["y"]);
      $("#id_height").val(cropData["height"]);
      $("#id_width").val(cropData["width"]);
      $("#modalCrop").modal("hide");
      $("#cover-submit").click();
      console.log($("#id_x").val());
      console.log($("#id_y").val())
      console.log($("#id_height").val())
      console.log($("#id_width").val())
      $("#cover_pic").submit();
    });
  });
