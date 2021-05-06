// var canvas = document.querySelector("canvas");
// var signaturePad = new SignaturePad(canvas);
// signaturePad.toDataURL("image/jpeg"); // save image as JPEG
// const data = signaturePad.toData();


var wrapper = document.getElementById("signature-pad");
var clearButton = wrapper.querySelector("[data-action=clear]");
// var changeColorButton = wrapper.querySelector("[data-action=change-color]");
// var undoButton = wrapper.querySelector("[data-action=undo]");
// var savePNGButton = wrapper.querySelector("[data-action=save-png]");
var saveJPGButton = wrapper.querySelector("[data-action=save-jpg]");
// var saveSVGButton = wrapper.querySelector("[data-action=save-svg]");
var canvas = wrapper.querySelector("canvas");
var botonGuardar = querySelector(".boton-guardar");
var signaturePad = new SignaturePad(canvas, {
  // It's Necessary to use an opaque color when saving image as JPEG;
  // this option can be omitted if only saving as PNG or SVG
  backgroundColor: 'rgb(255, 255, 255)'
});
signaturePad.toDataURL("image/jpeg"); // save image as JPEG

// Adjust canvas coordinate space taking into account pixel ratio,
// to make it look crisp on mobile devices.
// This also causes canvas to be cleared.
function resizeCanvas() {
  // When zoomed out to less than 100%, for some very strange reason,
  // some browsers report devicePixelRatio as less than 1
  // and only part of the canvas is cleared then.
  var ratio =  Math.max(window.devicePixelRatio || 1, 1);

  // This part causes the canvas to be cleared
  canvas.width = canvas.offsetWidth * ratio;
  canvas.height = canvas.offsetHeight * ratio;
  canvas.getContext("2d").scale(ratio, ratio);

  // This library does not listen for canvas changes, so after the canvas is automatically
  // cleared by the browser, SignaturePad#isEmpty might still return false, even though the
  // canvas looks empty, because the internal data of this library wasn't cleared. To make sure
  // that the state of this library is consistent with visual state of the canvas, you
  // have to clear it manually.
  signaturePad.clear();
}

// On mobile devices it might make more sense to listen to orientation change,
// rather than window resize events.
window.onresize = resizeCanvas;
resizeCanvas();


// Aca tiene que crear un nuevo Data Form que tenga todas las cosas del form,
// crear un file tipo imagen con  'firma-'+ nombre/secuencia del ot + '.jpg'  y enviarlo
// despues lo manejo desde el servidor
function download(dataURL, filename) {
  var blob = dataURLToBlob(dataURL);
  var url = window.URL.createObjectURL(blob);

  var a = document.createElement("a");
  a.style = "display: none";
  a.href = url;
  a.download = filename;

  document.body.appendChild(a);
  a.click();

  window.URL.revokeObjectURL(url);
}

// One could simply use Canvas#toBlob method instead, but it's just to show
// that it can be done using result of SignaturePad#toDataURL.
function dataURLToBlob(dataURL) {
  // Code taken from https://github.com/ebidel/filer.js
  var parts = dataURL.split(';base64,');
  var contentType = parts[0].split(":")[1];
  var raw = window.atob(parts[1]);
  var rawLength = raw.length;
  var uInt8Array = new Uint8Array(rawLength);

  for (var i = 0; i < rawLength; ++i) {
    uInt8Array[i] = raw.charCodeAt(i);
  }

  return new Blob([uInt8Array], { type: contentType });
}

botonGuardar.addEventListener("click", function (event) {
  if (signaturePad.isEmpty()) {
    alert("Please provide a signature first.");
  } else {
    var dataURL = signaturePad.toDataURL("image/jpeg");
    download(dataURL, "signature.jpg");
  }
});
saveJPGButton.addEventListener("click", function (event) {
  if (signaturePad.isEmpty()) {
    alert("Please provide a signature first.");
  } else {
    var dataURL = signaturePad.toDataURL("image/jpeg");
    download(dataURL, "signature.jpg");
  }
});
//</==================================================================================/>
function dataURLToBlob(dataURL) {
  // Code taken from https://github.com/ebidel/filer.js
  var parts = dataURL.split(';base64,');
  var contentType = parts[0].split(":")[1];
  var raw = window.atob(parts[1]);
  var rawLength = raw.length;
  var uInt8Array = new Uint8Array(rawLength);

  for (var i = 0; i < rawLength; ++i) {
    uInt8Array[i] = raw.charCodeAt(i);
  }
  return new Blob([uInt8Array], { type: contentType });
}

function firmar(){
  var wrapper = document.getElementById("signature-pad");
  var canvas = wrapper.querySelector("canvas");
  var botonGuardar = document.querySelector(".boton-guardar");
  var botonLimpiar = document.querySelector(".boton-limpiar");
  var form = document.getElementById('orden_form');
  var signaturePad = new SignaturePad(canvas, {
    backgroundColor: 'rgb(255, 255, 255)'
  });
  botonLimpiar.addEventListener("click", function (event) {
    signaturePad.clear();
  });
  botonGuardar.addEventListener("click", function (event) {
    if (signaturePad.isEmpty()) {
      alert("Please provide a signature first.");
    } else {
      base64_file = signaturePad.toDataURL("image/jpeg");
      blob = dataURLToBlob(base64_file)
      var file = new File([blob], "signature.jpg", { type: "image/jpeg", lastModified: Date.now() });
      console.log(file)
      form_data = new FormData(form);
      form_data.set('firma_archivo',file);
      form_data.set('firma_archivo_nombre','nombre_archivo.jpeg');
      var request = new XMLHttpRequest();
      request.open("POST", "/odtindividual/4/guardar");
      request.send(form_data);
    }
  });
  function resizeCanvas() {

    var ratio =  Math.max(window.devicePixelRatio || 1, 1);

    canvas.width = canvas.offsetWidth * ratio;
    canvas.height = canvas.offsetHeight * ratio;
    canvas.getContext("2d").scale(ratio, ratio);

    signaturePad.clear();
  }
  resizeCanvas();
}


// SEARCH
//</==================================================================================/>

var maquina_nueva_counter = 0;  //tiene que ser una variable global
function anadir_maquina(){

  var nuevo_data = "nuevo-"+maquina_nueva_counter;

  maquina = document.createElement('DIV');
  maquina.className="orden-maquinas_lista_item";
  maquina.dataset.maquinaId = nuevo_data;

  maquinaInput = document.createElement('INPUT');
  maquinaInput.type = "text";
  maquinaInput.className = "buscar-maquina";
  // maquinaInput.name = 'maquina_item--nuevo-'+maquina_nueva_counter;
  maquinaInput.addEventListener('keyup',function(){elementSearch(nuevo_data,'maquina')}, false)
  maquinaInput.addEventListener('focus',elementSearch, false)
  maquinaInput.addEventListener('focusout',cancelSearch, false)

  maquinaInputId = document.createElement('INPUT');
  maquinaInputId.type = "text";
  maquinaInputId.className = "buscar-maquina-id";
  maquinaInputId.name = 'maquina_item--nuevo-'+maquina_nueva_counter;

  maquinaBorrar = document.createElement('DIV')
  maquinaBorrar.innerHTML = "[Borrar]"
  maquinaBorrar.className = "maquina_lista_item_borrar"
  maquinaBorrar.setAttribute("onClick","borrar_maquina(\'"+nuevo_data+"\')")

  maquinaBusqueda = document.createElement('UL')
  maquinaBusqueda.className = "lista_busqueda_maquina"

  maquina.appendChild(maquinaInput)
  maquina.appendChild(maquinaInputId)
  maquina.appendChild(maquinaBorrar)
  maquina.appendChild(maquinaBusqueda)

  lista_maquinas = document.querySelector('.orden-maquinas_lista');
  lista_maquinas.appendChild(maquina);
  maquina_nueva_counter++;
}

var productos_nuevo_counter = 0;  //tiene que ser una variable global
function anadir_producto(){
  var nuevo_data = "nuevo-"+productos_nuevo_counter;

  var producto = document.createElement('DIV')
  producto.className = "orden-producto_consumido_item"
  producto.dataset.productoConsumidoId = nuevo_data

  var productoInput = document.createElement('INPUT')
  productoInput.type = "text"
  productoInput.className = "buscar-producto-consumido"
  productoInput.addEventListener('keyup',function(){elementSearch(nuevo_data,'producto-consumido')}, false)
  productoInput.addEventListener('focus',elementSearch, false)
  productoInput.addEventListener('focusout',cancelSearch, false)

  var productoInputId = document.createElement('INPUT')
  productoInputId.type = "text"
  productoInputId.className = "buscar-producto-consumido-id"
  productoInputId.name = `producto_item_nuevo--${nuevo_data}`

  var productoInputCantidad = document.createElement('INPUT')
  productoInputCantidad.type = "text"
  productoInputCantidad.name= `cantidad_producto_nuevo--${nuevo_data}`

  var productoBusqueda = document.createElement('UL')
  productoBusqueda.className = "lista_busqueda_producto-consumido"

  var productoBorrar = document.createElement('DIV')
  productoBorrar.className = "producto_lista_item_borrar"
  productoBorrar.innerHTML = "[Borrar]"
  productoBorrar.setAttribute( "onClick", `borrar_producto(\'${nuevo_data}\')`);

  producto.appendChild(productoInput)
  producto.appendChild(productoInputId)
  producto.appendChild(productoInputCantidad)
  producto.appendChild(productoBorrar)
  producto.appendChild(productoBusqueda)

  lista_productos = document.querySelector('.orden-productos_lista_body');
  lista_productos.appendChild(producto);
  productos_nuevo_counter++;
}

function elementSearch(item_data, tipo){
  // data-producto-id o data-maquina-id
  console.log('-----------------parametros--------------------')
  console.log(`data: ${item_data}, tipo:${tipo}`)
  item = document.querySelector("[data-"+tipo+"-id=\'"+item_data+"\']")
  console.log('-----------------item--------------------')
  console.log(item)
  input_element = item.querySelector(`.buscar-${tipo}`)
  console.log('-------------tipo busqueda---------------')
  console.log(tipo)
  input_value = input_element.value
  // type si el input tiene data-tipo = 'maquina' o 'producto' y lo añado a la url como get
  // generar la clase del searchList dinamicamente si es maquina o producto (necesitaria un data en realidad)
  searchList = item.querySelector(`.lista_busqueda_${tipo}`)
  if (input_value.length >= 3){
    Url = `/buscarelemento?input=${input_value}&tipo=${tipo}`
    // console.log(input);
    // fetch de busqueda

     fetch(Url).then(data=>{return data.json()})
    .then(res => {
      // limpiar la lista
      while (searchList.firstChild) {
        searchList.removeChild(searchList.firstChild);
      }
      console.log(res)
      let elementos = res['elementos']
      // console.log(series)

      if (elementos.length > 0){
        if (!searchList.classList.contains('active')){
          searchList.classList.add('active')
        }
        elementos.forEach(function(elemento){
          listLi = document.createElement('LI')
          // cada una on click tiene que agarrar su div y darle el valor que esta buscando y cerrar la busqueda
          // si es identico al valor que ya está que no aparezca la lista
          searchInfo = document.createElement('DIV')
          searchInfo.className = 'search-item-info'
          searchInfo.innerHTML = elemento[1] //es el nombre
          // searchInfo.setAttribute("onClick",function(){ seleccionar_maquina(elemento) } )
          elemento_id = elemento[0]
          elemento_name = elemento[1]
          searchInfo.setAttribute("onClick","seleccionar_elemento(\'"+elemento_id+"\',\'"+elemento_name+"\',\'"+item_data+"\',\'"+tipo+"\')")
          listLi.appendChild(searchInfo)
          searchList.appendChild(listLi)
        })
      }
    })
  } else {
    cancelSearch(item_data, tipo)
  }
}

function seleccionar_elemento(id, name, item_data, tipo){
  item = document.querySelector("[data-"+tipo+"-id=\'"+item_data+"\']")
  item.querySelector(`.buscar-${tipo}`).value = name;
  item.querySelector(`.buscar-${tipo}-id`).value = id;
  cancelSearch(item_data,tipo)
}

function cancelSearch(item_data, tipo){
  console.log('cancel search')
  item = document.querySelector("[data-"+tipo+"-id=\'"+item_data+"\']")
  setTimeout(function(){
      searchList = item.querySelector(`.lista_busqueda_${tipo}`)
      // borrar items
      while (searchList.firstChild) {
        searchList.removeChild(searchList.firstChild);
      }
      // desactivar clase active
      if (searchList.classList.contains('active')){
        searchList.classList.remove('active')
      }
    },100)
}

function cargarEventListeners(){
  productos = document.querySelectorAll('.orden-producto_consumido_item');
  maquinas = document.querySelectorAll('.orden-maquinas_lista_item');
  productos.forEach(function(prod){
    data = prod.dataset.productoConsumidoId
    // se lo estas cargando directamente a al div padre, no al input que necesito
    console.log(`prod: ${prod},data: ${data}`)
    input = prod.querySelector('.buscar-producto-consumido')
    input.addEventListener('keyup',function(){elementSearch(prod.dataset.productoConsumidoId,'producto-consumido')}, false)
    // input.addEventListener('focus',elementSearch, false)
    // input.addEventListener('focusout',cancelSearch, false)
  });
  maquinas.forEach(function(maq){
    data = maq.dataset.maquinaId
    input = maq.querySelector('.buscar-maquina')
    input.addEventListener('keyup',function(){elementSearch(maq.dataset.maquinaId,'maquina')}, false)
    // input.addEventListener('focus',elementSearch, false)
    // input.addEventListener('focusout',cancelSearch, false)
  });
}

// funcion que añada estos tres a los elementos ya existentes
document.querySelector('#buscar-maquina-wrapper').addEventListener('keyup',elementSearch, false)
document.querySelector('#buscar-maquina').addEventListener('focus',elementSearch, false)
document.querySelector('#buscar-maquina-wrapper').addEventListener('focusout',cancelSearch, false)


// =======================================================================================================================
var wrapper = document.getElementById("signature-pad");
var canvas = wrapper.querySelector("canvas");

function resizeCanvas() {
  // When zoomed out to less than 100%, for some very strange reason,
  // some browsers report devicePixelRatio as less than 1
  // and only part of the canvas is cleared then.
  var ratio =  Math.max(window.devicePixelRatio || 1, 1);

  // This part causes the canvas to be cleared
  canvas.width = canvas.offsetWidth * ratio;
  canvas.height = canvas.offsetHeight * ratio;
  canvas.getContext("2d").scale(ratio, ratio);

  // This library does not listen for canvas changes, so after the canvas is automatically
  // cleared by the browser, SignaturePad#isEmpty might still return false, even though the
  // canvas looks empty, because the internal data of this library wasn't cleared. To make sure
  // that the state of this library is consistent with visual state of the canvas, you
  // have to clear it manually.
  signaturePad.clear();
}
