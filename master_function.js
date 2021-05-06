
var producto_consumido_nuevo_counter = 0;  //tiene que ser una variable global
var maquina_utilizada_nueva_counter = 0;  //tiene que ser una variable global
var movilidad_utilizada_nueva_counter = 0;  //tiene que ser una variable global
var mano_obra_nuevo_counter = 0;  //tiene que ser una variable global
var tipo_trabajo_nuevo_counter = 0;  //tiene que ser una variable global
var extra_nuevo_counter = 0;  //tiene que ser una variable global
var promotor_nuevo_counter = 0;

function borrar_elemento(nombreElemento, elementoId){
stringSelector = `[data-${nombreElemento}-id=\'${elementoId}\']`
console.log(stringSelector)
elemento = document.querySelector(stringSelector);
elemento.parentNode.removeChild(elemento);
}

function to_camel(s){
return s.replace(/([-_][a-z])/ig, ($1) => {
    return $1.toUpperCase()
    .replace('-', '')
    .replace('_', '');
});
}

function anadir_elemento(nombreElemento, counter, cantidad=null, responsable=null) {
    console.log('-----------------------------------')
    console.log(nombreElemento)
    console.log(counter)
    var nuevo_data = "nuevo-" + counter;
    elemento = document.createElement('DIV');
    elemento.className = `orden-${nombreElemento}_item`;
    elemento.setAttribute(`data-${nombreElemento}-id` ,nuevo_data);

    // este es el nombre, tambien lo llevan todos, no es necesario verificar
    elementoInput = document.createElement('INPUT');
    elementoInput.type = "text";
    elementoInput.className = `buscar-${nombreElemento} input_field`;
    elementoInput.addEventListener('keyup',function(){elementSearch(nuevo_data,nombreElemento)}, false)
    elementoInput.addEventListener('focus',elementSearch, false)
    elementoInput.addEventListener('focusout',cancelSearch, false)

    // lo llevan todos, no es necesario verificar
    elementoInputId = document.createElement('INPUT');
    elementoInputId.type = "text";
    elementoInputId.className = `buscar-${nombreElemento}-id`;
    elementoInputId.name = `${nombreElemento}_item--nuevo-${counter}`;

    // tambien todos llevan borrar
    elementoBorrar = document.createElement('DIV')
    elementoBorrar.className = `${nombreElemento}_borrar borrar-elemento`
    // TODO: la funcion borrar elemento tambien tiene que ser usada por todos
    // elementoBorrar.setAttribute("onClick",`borrar_${nombreElemento}(\'`+nuevo_data+"\')")
    elementoBorrar.setAttribute("onClick",`borrar_elemento(\'${nombreElemento}\',\'${nuevo_data}\')`)
    elementoBorrarIcon = document.createElement('I')
    elementoBorrarIcon.className = "far fa-trash-alt"
    elementoBorrar.appendChild(elementoBorrarIcon)

    elementoBusqueda = document.createElement('UL')
    elementoBusqueda.className = `lista_busqueda_${nombreElemento}`

    elemento.appendChild(elementoInput)
    elemento.appendChild(elementoInputId)

    if (responsable){
        // hacer un fetch para traer el responsable_id
        var elementoInputResponsable = document.createElement('INPUT')
        elementoInputResponsable.type = "text"
        elementoInputResponsable.className = `buscar-${nombreElemento}_responsable`;
        //elementoInputResponsable.name= `cantidad_${nombreElemento}--${nuevo_data}`
        elemento.appendChild(elementoInputResponsable)
    }


    if (cantidad){
        var elementoInputCantidad = document.createElement('INPUT')
        
        elementoCantidadContainer = document.createElement('DIV')
        elementoCantidadContainer.className = "cantidad-uom"

        elementoInputCantidad.type = "text"
        // elementoInputCantidad.className = `${nombreElemento}_cantidad`
        elementoInputCantidad.className = 'input_field'
        elementoInputCantidad.name= `cantidad_${nombreElemento}--${nuevo_data}`

        elementoUom = document.createElement('DIV')
        elementoUom.className = `${nombreElemento}_uom`
        elementoUom.innerHTML = 'uom'

        elementoCantidadContainer.appendChild(elementoInputCantidad)
        elementoCantidadContainer.appendChild(elementoUom)

        elemento.appendChild(elementoCantidadContainer)
    }


    elemento.appendChild(elementoBorrar)
    elemento.appendChild(elementoBusqueda)

    lista_elementos = document.querySelector(`.orden-${nombreElemento}_lista_body`);
    lista_elementos.appendChild(elemento);
    add_counter(nombreElemento)
}

function get_uom(prdocut_id){
Url = `/buscaruom?id=${productid}`
    fetch(Url).then(data=>{return data.json()})
    .then(res => {
        console.log('---------------')
        console.log(res['uom'])
        return res['uom']
    })
}

function add_counter(nombreElemento) {
    switch (nombreElemento) {
        case "tipo_trabajo":
            window.tipo_trabajo_nuevo_counter++
            break;
        case "mano_obra_utilizada":
            window.mano_obra_nuevo_counter++
            break;
        case "producto_consumido":
            window.producto_consumido_nuevo_counter++;
            break;
        case "maquina_utilizada":
            window.maquina_utilizada_nueva_counter++;
            break;
        case "movilidad_utilizada":
            window.movilidad_utilizada_nueva_counter++;
            break;
        case "extra":
            window.extra_nuevo_counter++;
            break;
        case "promotor":
            window.promotor_nuevo_counter++;
            break;
        default:
            console.log('Hit default');
    }
}

function get_counter(nombreElemento){
    console.log(nombreElemento)
    switch (nombreElemento) {
        case "tipo_trabajo":
            return window.tipo_trabajo_nuevo_counter
            break;
        case "mano_obra_utilizada":
            return window.mano_obra_nuevo_counter
            break;
        case "producto_consumido":
            return window.producto_consumido_nuevo_counter;
            break;
        case "maquina_utilizada":
            return window.maquina_utilizada_nueva_counter;
            break;
        case "movilidad_utilizada":
            return window.movilidad_utilizada_nueva_counter;
            break;
        case "extra":
            return window.extra_nuevo_counter;
            break;
        case "promotor":
            return window.promotor_nuevo_counter;
            break;
        default:
            console.log('Hit default');
    }
}

function elementSearch(item_data, tipo){
    // data-producto-id o data-maquina-id
    //console.log("[data-"+tipo+"-id=\'"+item_data+"\']")
    item = document.querySelector("[data-"+tipo+"-id=\'"+item_data+"\']")
    input_element = item.querySelector(`.buscar-${tipo}`)
    input_value = input_element.value
    //console.log(`item: ${item}`)
    //console.log(`input_element: ${input_element}`)
    //console.log(`input_value: ${input_value}`)
    // type si el input tiene data-tipo = 'maquina' o 'producto' y lo añado a la url como get
    // generar la clase del searchList dinamicamente si es maquina o producto (necesitaria un data en realidad)
    searchList = item.querySelector(`.lista_busqueda_${tipo}`)
    if (input_value.length >= 3){
      Url = `/buscarelemento?input=${input_value}&amp;tipo=${tipo}`
      // console.log(input);
      // fetch de busqueda
      if (tipo=='producto_consumido') {
        uom = (elemento[2]) ? elemento[2] : ''
      }
       fetch(Url).then(data=>{return data.json()})
      .then(res => {
        // limpiar la lista
        while (searchList.firstChild) {
          searchList.removeChild(searchList.firstChild);
        }
        console.log(res)
        let elementos = res['elementos']

        if (elementos.length > 0){
          if (!searchList.classList.contains('active')){
            searchList.classList.add('active')
          }
          elementos.forEach(function(elemento){
            listLi = document.createElement('LI')
            searchInfo = document.createElement('DIV')
            searchInfo.className = 'search-item-info'
            searchInfo.innerHTML = elemento[1] //es el nombre
            elemento_id = elemento[0]
            elemento_name = elemento[1]
            responsable = ''
            if (tipo=='maquina_utilizada' || tipo=='movilidad_utilizada') {
              responsable = (elemento[2]) ? elemento[2] : ''
            }
            uom = ''
            console.log(`responsable antes de bla bla ---------: ${responsable}`)
            if(tipo === 'rubro'){
                item.querySelector(`.buscar-${tipo}-id`).value = '';
            }
            searchInfo.setAttribute("onClick","seleccionar_elemento(\'"+elemento_id+"\',\'"+elemento_name+"\',\'"+item_data+"\',\'"+tipo+"\',\'"+responsable+"\',\'"+uom+"\')")
            listLi.appendChild(searchInfo)
            searchList.appendChild(listLi)
          })
        }
      })
    } else {
      cancelSearch(item_data, tipo)
    }
  }



function seleccionar_elemento(id, name, item_data, tipo, responsable=false, uom=false){
console.log("--------funcion seleccionar_elemento--------")
item = document.querySelector("[data-"+tipo+"-id=\'"+item_data+"\']")
item.querySelector(`.buscar-${tipo}`).value = name;
item.querySelector(`.buscar-${tipo}-id`).value = id;
console.log(`responsable en seleccion: ${responsable}`)
if (responsable) {
    console.log(`clase buscada: .buscar-${tipo}_responsable`)
    item.querySelector(`.buscar-${tipo}_responsable`).value = responsable;
}
if (tipo==='producto_consumido') {
    console.log('........es producto consumido, cambiar uom')
    item.querySelector(`.${tipo}_uom`).innerHTML = uom
}
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
mano_obra_utilizadas = document.querySelectorAll('.orden-mano_obra_utilizada_item');
tipos_trabajo = document.querySelectorAll('.orden-tipo_trabajo_item');
productos = document.querySelectorAll('.orden-producto_consumido_item');
maquinas = document.querySelectorAll('.orden-maquina_utilizada_item');
movilidades = document.querySelectorAll('.orden-movilidad_utilizada_item');
extras = document.querySelectorAll('.orden-extra_item');


//mano_obra_utilizadas.forEach(function(mo){
//  data = mo.dataset.mano_obra_utilizadaId
//  input = mo.querySelector('.buscar-mano_obra_utilizada')
//  input.addEventListener('keyup',function(){elementSearch(mo.dataset.mano_obra_utilizadaId,'mano_obra_utilizada')}, false)
//});

//tipos_trabajo.forEach(function(tt){
//  data = tt.dataset.tipo_trabajoId
//  input = tt.querySelector('.buscar-tipo_trabajo')
//  input.addEventListener('keyup',function(){elementSearch(tt.dataset.tipo_trabajoId,'tipo_trabajo')}, false)
//});

productos.forEach(function(prod){
    data = prod.dataset.producto_consumidoId
    //console.log(`prod: ${prod},data: ${data}`)
    input = prod.querySelector('.buscar-producto_consumido')
    input.addEventListener('keyup',function(){elementSearch(prod.dataset.producto_consumidoId,'producto_consumido')}, false)
});

//maquinas.forEach(function(maq){
//  data = maq.dataset.maquina_utilizadaId
//  input = maq.querySelector('.buscar-maquina_utilizada')
//  input.addEventListener('keyup',function(){elementSearch(maq.dataset.maquina_utilizadaId,'maquina_utilizada')}, false)
//});

//movilidades.forEach(function(mov){
//  data = mov.dataset.movilidad_utilizadaId
//  input = mov.querySelector('.buscar-movilidad_utilizada')
//  input.addEventListener('keyup',function(){elementSearch(mov.dataset.movilidad_utilizadaId,'movilidad_utilizada')}, false)
//});
//extras.forEach(function(ext){
//  data = ext.dataset.extraId
//  input = ext.querySelector('.buscar-extra')
//  input.addEventListener('keyup',function(){elementSearch(ext.dataset.extraId,'extra')}, false)
//});
}

function anadir_elemento_select(nombreElemento, counter, cantidad=null, responsable=null) {
    console.log('-----------------------------------')
    console.log(nombreElemento)
    console.log(counter)
    var nuevo_data = "nuevo-" + counter;
    elemento = document.createElement('DIV');
    elemento.className = `orden-${nombreElemento}_item`;
    // elemento.dataset.tipoTrabajoId = nuevo_data;
    elemento.setAttribute(`data-${nombreElemento}-id` ,nuevo_data);

    // crear elemento select y primera opcion vacia
    elementoSelect = document.createElement('SELECT');
    elementoSelect.name = `${nombreElemento}_item--nuevo-${counter}`;
    elementoSelect.className = 'input_field';
    //elementoSelect.addEventListener('change',function(){onchange_select(event, nombreElemento, nuevo_data)}, false)
    optionVacia = document.createElement('OPTION')
    elementoSelect.appendChild(optionVacia)

    // fetch de la lista de opciones (llamo a element search?),
    // deberia pero hace otras cosas que no deberia y no quiero ponerme a separarla ahora
    input_value = '';
    Url = `/buscarelemento?input=${input_value}&amp;tipo=${nombreElemento}`
    fetch(Url).then(data=>{return data.json()})
    .then(res => {
        console.log(res)
        let elementos = res['elementos']
        //selectList = document.querySelector("[name='promotor_item--1']")
        elementos.forEach(function(elemento){
            console.log(elemento)
            optionElement = document.createElement('OPTION');
            optionElement.value = elemento[0];  // el id del elemento
            optionElement.innerHTML = elemento[1];  // el nombre del elemento
            elementoSelect.appendChild(optionElement);
        })
    })

    elemento.appendChild(elementoSelect)

    if (responsable){
        // añade el evento onchange y cambia el responsable
        elementoSelect.addEventListener('change',function(){onchange_select(event, nombreElemento, nuevo_data)}, false)
        // hacer un fetch para traer el responsable_id
        var elementoResponsable = document.createElement('DIV')
        elementoResponsable.className = `buscar-${nombreElemento}_responsable responsable`;
        elementoResponsable.innerHTML = 'responsable'

        // elemento.appendChild(elementoResponsable)
    }

    //cantidad
    if (cantidad){
        var elementoInputCantidad = document.createElement('INPUT')
        elementoInputCantidad.type = "text"
        elementoInputCantidad.className = 'input_field';
        elementoInputCantidad.name= `cantidad_${nombreElemento}--${nuevo_data}`

        elemento.appendChild(elementoInputCantidad)
    }

    // tambien todos llevan borrar
    elementoBorrar = document.createElement('DIV')
    elementoBorrar.className = `${nombreElemento}_borrar borrar-elemento`
    // TODO: la funcion borrar elemento tambien tiene que ser usada por todos
    // elementoBorrar.setAttribute("onClick",`borrar_${nombreElemento}(\'`+nuevo_data+"\')")
    elementoBorrar.setAttribute("onClick",`borrar_elemento('${nombreElemento}',\'${nuevo_data}\')`)
    elementoBorrarIcon = document.createElement('I')
    elementoBorrarIcon.className = "far fa-trash-alt"
    elementoBorrar.appendChild(elementoBorrarIcon)

    elemento.appendChild(elementoBorrar)

    lista_elementos = document.querySelector(`.orden-${nombreElemento}_lista_body`);
    lista_elementos.appendChild(elemento);
    if (responsable){
    insertAfter(elementoResponsable, elemento)
    }
    add_counter(nombreElemento)
}

function onchange_select(event, nombreElemento, data_id){
    console.log('onchange select')
    item = document.querySelector(`[data-${nombreElemento}-id = '${data_id}']`)
    console.log('item', item)
    id = event.target.value
    console.log('id', id)
    Url = `/buscarresponsable?id=${id}&amp;tipo=${nombreElemento}`
    fetch(Url).then(data=>{return data.json()})
    .then(res => {
        responsable_field = item.querySelector(`.${nombreElemento}_responsable`)
        responsable_field.innerHTML = `Responsable: ${res['elementos'][0]}`
    })
}

function insertAfter(newNode, referenceNode) {
referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}
