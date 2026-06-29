// ================= SEGURIDAD Y SESIÓN =================
function verificarSesion() {
    const isLogged = sessionStorage.getItem('logico_auth');
    const isLoginPage = window.location.pathname.includes('index.html') || window.location.pathname.endsWith('/');
    
    if (!isLogged && !isLoginPage) window.location.href = 'index.html'; 
    else if (isLogged && isLoginPage) window.location.href = 'farmacias.html'; 
}

function iniciarSesion() {
    const user = document.getElementById('userLogin').value;
    const pass = document.getElementById('passLogin').value;
    
    if(user === 'admin' && pass === '1234') {
        sessionStorage.setItem('logico_auth', 'true');
        inicializarBaseDeDatos();
        window.location.href = 'farmacias.html';
    } else {
        alert('Credenciales incorrectas. Usa admin / 1234');
    }
}

function cerrarSesion() {
    sessionStorage.removeItem('logico_auth');
    window.location.href = 'index.html';
}

// ================= BASE DE DATOS LOCAL =================
function inicializarBaseDeDatos() {
    if (!localStorage.getItem('dbFarmacias')) {
        localStorage.setItem('dbFarmacias', JSON.stringify([
            { id: 1, codigo: "CV-RM", nombre: "Cruz Verde Las Condes", region: "Región Metropolitana de Santiago", provincia: "Santiago", estado: "Activa" },
            { id: 2, codigo: "AH-VAL", nombre: "Ahumada Viña del Mar", region: "Valparaíso", provincia: "Valparaíso", estado: "Activa" }
        ]));
    }
    if (!localStorage.getItem('dbMotoristas')) {
        localStorage.setItem('dbMotoristas', JSON.stringify([
            { id: 1, nombre: "Carlos Méndez", rut: "15.234.789-K", region: "Región Metropolitana de Santiago", provincia: "Santiago", estado: "Activo", patente: "" }
        ]));
    }
}

// ================= GEOGRAFÍA =================
const bdRegiones = {
    "Región Metropolitana de Santiago": ["Santiago", "Cordillera", "Maipo", "Talagante", "Melipilla", "Chacabuco"],
    "Valparaíso": ["Valparaíso", "San Antonio", "Quillota", "Marga Marga", "Los Andes", "San Felipe", "Petorca"],
    "Biobío": ["Concepción", "Arauco", "Biobío"]
};

function cargarSelectRegiones(datalistId) {
    const datalist = document.getElementById(datalistId);
    if(!datalist) return;
    datalist.innerHTML = ''; 
    Object.keys(bdRegiones).forEach(r => datalist.innerHTML += `<option value="${r}">`);
}

function cargarProvincias(inputIdRegion, datalistIdProvincia, inputIdProvincia) {
    const regionSeleccionada = document.getElementById(inputIdRegion).value;
    const datalistProv = document.getElementById(datalistIdProvincia);
    const inputProv = document.getElementById(inputIdProvincia);
    
    if(!datalistProv || !inputProv) return;
    datalistProv.innerHTML = ''; 
    inputProv.value = ''; 
    
    if(bdRegiones[regionSeleccionada]) {
        bdRegiones[regionSeleccionada].forEach(p => datalistProv.innerHTML += `<option value="${p}">`);
    }
}

// ================= RUT =================
function validarRUT(rut) {
    let valor = rut.replace(/\./g, '').replace(/-/g, '').toUpperCase();
    if (valor.length < 2) return false;
    let cuerpo = valor.slice(0, -1);
    let dv = valor.slice(-1);
    if (!cuerpo.match(/^[0-9]+$/)) return false;
    let suma = 0; let multiplo = 2;
    for (let i = 1; i <= cuerpo.length; i++) {
        let index = multiplo * valor.charAt(cuerpo.length - i);
        suma = suma + index;
        if (multiplo < 7) { multiplo = multiplo + 1; } else { multiplo = 2; }
    }
    let dvEsperado = 11 - (suma % 11);
    dvEsperado = (dvEsperado == 11) ? "0" : (dvEsperado == 10) ? "K" : dvEsperado.toString();
    return dv === dvEsperado;
}

function darFormatoRUT(input) {
    let valor = input.value.replace(/\./g, '').replace(/-/g, '');
    if (valor.length > 1) {
        let cuerpo = valor.slice(0, -1);
        let dv = valor.slice(-1).toUpperCase();
        cuerpo = cuerpo.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
        input.value = `${cuerpo}-${dv}`;
    } else {
        input.value = valor;
    }
}

// ================= INIT =================
document.addEventListener('DOMContentLoaded', () => {
    verificarSesion();
    if(document.getElementById('listaRegionesFarmacia')) cargarSelectRegiones('listaRegionesFarmacia');
    if(document.getElementById('listaRegionesMotorista')) cargarSelectRegiones('listaRegionesMotorista');
    if(document.getElementById('listaRegionesMov')) cargarSelectRegiones('listaRegionesMov');

    const inputRut = document.getElementById('m_rut');
    if(inputRut) inputRut.addEventListener('input', function() { darFormatoRUT(this); });
});