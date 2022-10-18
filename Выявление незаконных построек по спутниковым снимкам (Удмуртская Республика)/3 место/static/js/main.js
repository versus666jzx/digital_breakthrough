$(document).ready(function () {
    $('#file-input').focus(function() {
        $('label').addClass('focus');
    })
    .focusout(function() {
        $('label').removeClass('focus');
    });

    var dropZone = $('#upload-container');
    let Data = new FormData();

    dropZone.on('dragover dragenter', function() {
        dropZone.addClass('dragover');
    });

    dropZone.on('dragleave', function(e) {
        dropZone.removeClass('dragover');
    });

    dropZone.on('dragleave', function(e) {
        let dx = e.pageX - dropZone.offset().left;
        let dy = e.pageY - dropZone.offset().top;
        if ((dx < 0) || (dx > dropZone.width()) || (dy < 0) || (dy > dropZone.height())) {
            dropZone.removeClass('dragover');
        };
    });

    dropZone.on('drop', function(e) {
        dropZone.removeClass('dragover');
        let files = e.originalEvent.dataTransfer.files;
        sendFiles(files);
    });

    $('#file-input').change(function() {
        let files = this.files;
        sendFiles(files);
    });

    function sendFiles(files) {
        let maxFileSize = 5242880;
        $(files).each(function(index, file) {
            if ((file.size <= maxFileSize) && ((file.type == 'image/png') || (file.type == 'image/jpeg'))) {
                Data.append('file', file);

                var reader  = new FileReader();
                reader.onload = function(e)  {
                    var image = document.createElement("img");
                    image.src = e.target.result;
                    $('#image_div').html(image);
                }
                reader.readAsDataURL(file);
            }
        });
    };

    $('#upload-container').submit(function(e) {
        e.preventDefault();

        $('.error').removeClass('error');

        if (validate(this)) {
            $(this).find('input').each(function(index, input) {
                if ($(input).attr('id') != 'file-input') {
                    Data.append($(input).attr('name'), $(input).val());
                }
            });

            $('#loader').css('display', 'flex');;
            $.ajax({
                url: dropZone.attr('action'),
                type: dropZone.attr('method'),
                data: Data,
                contentType: false,
                processData: false,
                success: function(data) {
                    $('html, body').animate({
                        scrollTop: $('#result').offset().top - 60
                    }, 300);

                    $('#loader').hide();

                    var dataJson = JSON.parse(data);

			        pic = new Image();

                    pic.onload = function() {
                        $('#result').append(
                            '<table class="result"><tr><th></th><th>Тип</th><th>Кадастровый номер</th><th>Адрес</th><th>Координаты</th><th>Bbox</th></tr></table>'
                        );

                        for (let objIndex in dataJson.coords) {
                            let obj = dataJson.coords[objIndex];
                            if (obj.rosreestr.error == undefined) {
                                let build = false;
                                let land = false;
                                let rows = obj.rosreestr.length;
                                for (const elemIndex in obj.rosreestr) {
                                    if (obj.rosreestr[elemIndex].type == 1) {
                                        land = true;
                                    }
                                    if (obj.rosreestr[elemIndex].type == 5) {
                                        build = true;
                                    }
                                    // obj.rosreestr[elemIndex].type - тип объекта (1, 2, 4, 5 и т.д.)
                                    let elem = obj.rosreestr[elemIndex];
                                    let address = elem.attrs.address != undefined ? elem.attrs.address : elem.attrs.name != undefined ? elem.attrs.name : '';
                                    $('table.result tbody').append('<tr class="object' + objIndex + '"><td>' + objIndex + '</td><td>' + elem.type + '</td><td>' + elem.attrs.cn + '</td><td>' + address + '</td></tr>');
                                }

                                $('table.result tbody tr.object' + objIndex).first().append('<td rowspan="' + rows + '">' + obj.coords.join(', ') + '</td>');

                                let idCanvas = 'canvas' + objIndex;
                                $('table.result tbody tr.object' + objIndex).first().append('<td rowspan="' + rows + '"><canvas height="300" width="300" id="' + idCanvas + '"></canvas></td>');

                                let canvasElem = document.getElementById(idCanvas),
                                ctx = canvasElem.getContext('2d');

                                ctx.drawImage(pic, 0, 0);

                                var bbox = obj.bbox;
                                ctx.strokeStyle = '#ff0000';
                                ctx.strokeRect(bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]);

                                if (build && land) {
                                    // Постройка зарегистрирована
                                    $('table.result tbody tr.object' + objIndex).css('background-color', '#ccff90');
                                } else if (land && !build) {
                                    // Земли пригодные для строительства, но здание не зарегистрировано
                                    $('table.result tbody tr.object' + objIndex).css('background-color', '#ffff8d');
                                } else {
                                    // Строительство запрещено
                                    $('table.result tbody tr.object' + objIndex).css('background-color', '#ff8a80');
                                }
                            } else {
                                $('table.result tbody').append('<tr><td colspan="4">' + obj.rosreestr.error + '</td></tr>');
                            }
                        }
                    }

                    pic.src = $('#image_div img').attr('src');
                },
                error: function(data) {
                    $('#loader').hide();
                }
            });
        }
    })

    function validate (formObj) {
        let errors = false;
        $(formObj).find('input').each(function(index, input) {
            if ($(input).val() == '') {
                if ($(input).attr('id') == 'file-input') {
                    $('#upload-image').addClass('error');
                } else {
                    $(input).addClass('error');
                }
                errors = true;
            }
        });

        return !errors;
    }
});