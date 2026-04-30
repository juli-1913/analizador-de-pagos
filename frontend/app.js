const API_URL = "https://analizador-de-pagos-production.up.railway.app";
let miGrafico = null;
let datosActuales = [];

/* =========================
   FECHAS / FORMATO
========================= */

function formatearFecha(fecha) {
  const dias = [
    "Domingo",
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
  ];

  const [anio, mes, dia] = fecha.split("-").map(Number);
  const f = new Date(anio, mes - 1, dia);

  const diaSemana = dias[f.getDay()];
  const anioCorto = String(anio).slice(-2);
  const fechaFormateada = `${dia}/${mes}/${anioCorto}`;

  return `${diaSemana} ${fechaFormateada}`;
}

function formatearFechaCorta(fecha) {
  const [anio, mes, dia] = fecha.split("-").map(Number);
  const anioCorto = String(anio).slice(-2);
  return `${dia}/${mes}/${anioCorto}`;
}

function obtenerNombreDia(fecha) {
  const dias = [
    "Domingo",
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
  ];

  const [anio, mes, dia] = fecha.split("-").map(Number);
  const f = new Date(anio, mes - 1, dia);
  return dias[f.getDay()];
}

function animarNumero(id, valorFinal, decimales = 0) {
  const elemento = document.getElementById(id);
  if (!elemento) return;

  let inicio = 0;
  const duracion = 800;
  const incremento = valorFinal / (duracion / 16);

  function actualizar() {
    inicio += incremento;

    if (inicio >= valorFinal) {
      elemento.textContent = `$${valorFinal.toLocaleString("es-AR", {
        minimumFractionDigits: decimales,
        maximumFractionDigits: decimales,
      })}`;
      return;
    }

    elemento.textContent = `$${inicio.toLocaleString("es-AR", {
      minimumFractionDigits: decimales,
      maximumFractionDigits: decimales,
    })}`;

    requestAnimationFrame(actualizar);
  }

  actualizar();
}

/* =========================
   TOKENS / AUTH
========================= */

function guardarAccessToken(token) {
  localStorage.setItem("access_token", token);
}

function getAccessToken() {
  return localStorage.getItem("access_token");
}

function guardarRefreshToken(token) {
  localStorage.setItem("refresh_token", token);
}

function getRefreshToken() {
  return localStorage.getItem("refresh_token");
}

function guardarTokens(accessToken, refreshToken) {
  guardarAccessToken(accessToken);
  if (refreshToken) {
    guardarRefreshToken(refreshToken);
  }
}

function limpiarTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

function mostrarAuthMensaje(mensaje, esError = false) {
  const authResultado = document.getElementById("authResultado");
  authResultado.innerHTML = `<p style="color:${esError ? "red" : "green"};">${mensaje}</p>`;
}

async function registrarse() {
  try {
    if (!validarRegistroVisual()) {
      actualizarBotonesAuth();
      return;
    }

    const nombre = document.getElementById("registroNombre").value.trim();
    const email = document.getElementById("registroEmail").value.trim();
    const password = document.getElementById("registroPassword").value.trim();
    const nombreComercio = document
      .getElementById("registroNombreComercio")
      .value.trim();

    const res = await fetch(`${API_URL}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        nombre,
        email,
        password,
        nombre_comercio: nombreComercio,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      mostrarRegistroMensaje(
        typeof data.detail === "string"
          ? data.detail
          : "No se pudo completar el registro",
        true
      );
      return;
    }

    // guarda sesión automáticamente
    guardarTokens(data.access_token, data.refresh_token);

    // obtiene usuario logueado
    const usuario = await authFetch(`${API_URL}/auth/me`);

    // muestra dashboard automáticamente
    mostrarSesion(usuario);

    // limpia inputs
    document.getElementById("registroNombre").value = "";
    document.getElementById("registroEmail").value = "";
    document.getElementById("registroPassword").value = "";
    document.getElementById("registroNombreComercio").value = "";

    mostrarRegistroMensaje("Cuenta creada correctamente");
  } catch (error) {
    console.error("Error en registrarse:", error);
    mostrarRegistroMensaje("Error de conexión en registro", true);
  }
}

async function login() {
  try {
    if (!validarLoginVisual()) {
      actualizarBotonesAuth();
      return;
    }
    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value.trim();

    if (!email || !password) {
      mostrarAuthMensaje("Completá email y contraseña", true);
      return;
    }

    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        password,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      mostrarAuthMensaje(
        typeof data.detail === "string"
          ? data.detail
          : "Email o contraseña incorrectos",
        true
      );
      return;
    }

    guardarTokens(data.access_token, data.refresh_token);
    const usuario = await authFetch(`${API_URL}/auth/me`);
    mostrarSesion(usuario);
    mostrarAuthMensaje("Sesión iniciada correctamente");
  } catch (error) {
    console.error("Error en login:", error);
    mostrarAuthMensaje("Error de conexión en login", true);
  }
}

async function refreshAccessToken() {
  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    throw new Error("No hay refresh token");
  }

  const res = await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      refresh_token: refreshToken,
    }),
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || "No se pudo refrescar la sesión");
  }

  guardarAccessToken(data.access_token);
  return data.access_token;
}

async function verMiSesion() {
  try {
    const data = await authFetch(`${API_URL}/auth/me`);
    mostrarSesion(data);
  } catch (error) {
    ocultarSesion();
  }
}

async function logout() {
  try {
    const refreshToken = getRefreshToken();

    if (refreshToken) {
      await fetch(`${API_URL}/auth/logout`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          refresh_token: refreshToken,
        }),
      });
    }

    limpiarTokens();
    limpiarCamposAuth();
    ocultarSesion();
    mostrarAuthMensaje("Sesión cerrada", true);

  } catch (error) {
    console.error("Error en logout:", error);

    limpiarTokens();
    limpiarCamposAuth();
    ocultarSesion();
    mostrarAuthMensaje("Sesión cerrada", true);
  }
}

async function authFetch(url, options = {}) {
  let accessToken = getAccessToken();

  const headers = {
    ...(options.headers || {}),
  };

  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }

  let res = await fetch(url, {
    ...options,
    headers,
  });

  if (res.status === 401) {
    try {
      accessToken = await refreshAccessToken();

      const retryHeaders = {
        ...(options.headers || {}),
        Authorization: `Bearer ${accessToken}`,
      };

      res = await fetch(url, {
        ...options,
        headers: retryHeaders,
      });
    } catch (error) {
      limpiarTokens();
      throw new Error("Sesión expirada. Volvé a iniciar sesión.");
    }
  }

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || "Error en la petición");
  }

  return data;
}



/* =========================
   PAGOS
========================= */

function limpiarFiltros() {
  document.getElementById("fechaDesde").value = "";
  document.getElementById("fechaHasta").value = "";
  listarPagos();
}

async function crearPago() {
  try {
    const monto = document.getElementById("monto").value;
    const fecha = document.getElementById("fecha").value;
    const estado = document.getElementById("estado").value.trim() || "pendiente";
    const resultado = document.getElementById("resultado");

    if (!monto || !fecha) {
      alert("Completá monto y fecha");
      return;
    }

    resultado.innerHTML = "<p>Cargando...</p>";

    const data = await authFetch(`${API_URL}/pagos`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        monto: Number(monto),
        fecha: fecha,
        estado: estado,
      }),
    });

    resultado.innerHTML = `
      <p class="success">Pago creado ID: ${data.id}</p>
      ${
        data.mp_init_point
          ? `<a href="${data.mp_init_point}" target="_blank">Ir a pagar</a>`
          : ""
      }
    `;

    document.getElementById("monto").value = "";
    document.getElementById("fecha").value = "";
    document.getElementById("estado").value = "";

    await listarPagos();

  } catch (error) {
    console.error(error);
    document.getElementById("resultado").innerHTML =
      `<p style="color:red;">${error.message}</p>`;
  }
}

function renderGraficoVentas(data) {
  const ventasPorFecha = {};

  data.forEach((p) => {
    if (p.estado === "pagado") {
      if (!ventasPorFecha[p.fecha]) {
        ventasPorFecha[p.fecha] = 0;
      }
      ventasPorFecha[p.fecha] += Number(p.monto);
    }
  });

  const fechasOrdenadas = Object.keys(ventasPorFecha).sort();

  const labels = fechasOrdenadas.map((fecha) => [
    obtenerNombreDia(fecha),
    `(${formatearFechaCorta(fecha)})`,
  ]);

  const valores = fechasOrdenadas.map((fecha) => ventasPorFecha[fecha]);

  const canvas = document.getElementById("graficoVentas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");

  if (miGrafico) {
    miGrafico.destroy();
  }

  miGrafico = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Ventas",
          data: valores,
          borderRadius: 8,
          backgroundColor: "#a8c5ff",
          hoverBackgroundColor: "#5b8def",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 800,
        easing: "easeOutQuart",
      },
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          callbacks: {
            title: function (context) {
              const index = context[0].dataIndex;
              const fecha = fechasOrdenadas[index];
              return `${obtenerNombreDia(fecha)} (${formatearFechaCorta(fecha)})`;
            },
            label: function (context) {
              return `Ventas: $${context.parsed.y.toLocaleString("es-AR")}`;
            },
          },
        },
      },
      scales: {
        x: {
          grid: {
            display: false,
          },
        },
        y: {
          beginAtZero: true,
          ticks: {
            callback: function (value) {
              return "$" + value.toLocaleString("es-AR");
            },
          },
        },
      },
    },
  });
}

function calcularResumenMensual(data) {
  const pagosPagados = data.filter((p) => p.estado === "pagado");

  if (pagosPagados.length === 0) {
    return {
      totalMesActual: 0,
      totalMesAnterior: 0,
      comparacionTexto: "-",
    };
  }

  let fechaMasReciente = pagosPagados[0].fecha;

  pagosPagados.forEach((p) => {
    if (p.fecha > fechaMasReciente) {
      fechaMasReciente = p.fecha;
    }
  });

  const [anioActual, mesActual] = fechaMasReciente.split("-").map(Number);

  let mesAnterior = mesActual - 1;
  let anioMesAnterior = anioActual;

  if (mesAnterior === 0) {
    mesAnterior = 12;
    anioMesAnterior -= 1;
  }

  let totalMesActual = 0;
  let totalMesAnterior = 0;

  pagosPagados.forEach((p) => {
    const [anio, mes] = p.fecha.split("-").map(Number);

    if (anio === anioActual && mes === mesActual) {
      totalMesActual += Number(p.monto);
    }

    if (anio === anioMesAnterior && mes === mesAnterior) {
      totalMesAnterior += Number(p.monto);
    }
  });

  let comparacionTexto = "-";

  if (totalMesAnterior === 0 && totalMesActual > 0) {
    comparacionTexto = "🟢 Mes actual sin base previa";
  } else if (totalMesAnterior === 0 && totalMesActual === 0) {
    comparacionTexto = "-";
  } else {
    const diferencia = totalMesActual - totalMesAnterior;
    const porcentaje = (diferencia / totalMesAnterior) * 100;
    const diferenciaFormateada = Math.abs(diferencia).toLocaleString("es-AR");

    if (diferencia > 0) {
      comparacionTexto = `🟢 +${porcentaje.toFixed(2)}% (+$${diferenciaFormateada})`;
    } else if (diferencia < 0) {
      comparacionTexto = `🔴 ${porcentaje.toFixed(2)}% (-$${diferenciaFormateada})`;
    } else {
      comparacionTexto = "⚖️ 0.00% ($0)";
    }
  }

  return {
    totalMesActual,
    totalMesAnterior,
    comparacionTexto,
  };
}

async function listarPagos() {
  try {
    const desde = document.getElementById("fechaDesde")?.value.trim();
    const hasta = document.getElementById("fechaHasta")?.value.trim();

    let url = `${API_URL}/pagos`;
    const params = new URLSearchParams();

    if (desde) params.append("desde", desde);
    if (hasta) params.append("hasta", hasta);

    if (params.toString()) {
      url += `?${params.toString()}`;
    }

    const data = await authFetch(url);
    datosActuales = Array.isArray(data) ? data : [];

    const tabla = document.getElementById("tablaPagos");
    tabla.innerHTML = "";

    if (!Array.isArray(data) || data.length === 0) {
      document.getElementById("total").textContent = "$0";
      document.getElementById("cantidad").textContent = "0";
      document.getElementById("pagados").textContent = "0";
      document.getElementById("pendientes").textContent = "0";
      document.getElementById("ticketPromedio").textContent = "$0";
      document.getElementById("mejorDia").textContent = "-";
      document.getElementById("peorDia").textContent = "-";
      document.getElementById("alertaVentas").textContent = "-";
      document.getElementById("mejorDiaSemana").textContent = "-";
      document.getElementById("peorDiaSemana").textContent = "-";
      document.getElementById("mesActual").textContent = "$0";
      document.getElementById("mesAnterior").textContent = "$0";
      document.getElementById("comparacionMensual").textContent = "-";

      renderGraficoVentas([]);
      tabla.innerHTML = `<tr><td colspan="4">No hay pagos</td></tr>`;
      return;
    }

    let total = 0;
    let pagados = 0;
    let pendientes = 0;

    data.forEach((p) => {
      if (p.estado === "pagado") {
        total += Number(p.monto);
        pagados++;
      }

      if (p.estado === "pendiente") {
        pendientes++;
      }
    });

    const ticketPromedio = pagados > 0 ? total / pagados : 0;

    animarNumero("total", total);
    document.getElementById("cantidad").textContent = data.length;
    document.getElementById("pagados").textContent = pagados;
    document.getElementById("pendientes").textContent = pendientes;
    animarNumero("ticketPromedio", ticketPromedio, 2);

    const resumenMensual = calcularResumenMensual(data);
    animarNumero("mesActual", resumenMensual.totalMesActual);
    animarNumero("mesAnterior", resumenMensual.totalMesAnterior);
    document.getElementById("comparacionMensual").textContent = resumenMensual.comparacionTexto;

    const ventasPorFecha = {};

    data.forEach((p) => {
      if (p.estado === "pagado") {
        if (!ventasPorFecha[p.fecha]) {
          ventasPorFecha[p.fecha] = 0;
        }
        ventasPorFecha[p.fecha] += Number(p.monto);
      }
    });

    let mejorDia = null;
    let peorDia = null;
    let maxVenta = -Infinity;
    let minVenta = Infinity;

    for (const fecha in ventasPorFecha) {
      const venta = ventasPorFecha[fecha];

      if (venta > maxVenta) {
        maxVenta = venta;
        mejorDia = fecha;
      }

      if (venta < minVenta) {
        minVenta = venta;
        peorDia = fecha;
      }
    }

    document.getElementById("mejorDia").textContent = mejorDia
      ? `${formatearFecha(mejorDia)} ($${maxVenta.toLocaleString("es-AR")})`
      : "-";

    document.getElementById("peorDia").textContent = peorDia
      ? `${formatearFecha(peorDia)} ($${minVenta.toLocaleString("es-AR")})`
      : "-";

    const fechas = Object.keys(ventasPorFecha).sort();
    let alertaTexto = "-";

    if (fechas.length >= 2) {
      const hoy = fechas[fechas.length - 1];
      const ayer = fechas[fechas.length - 2];

      const ventaHoy = ventasPorFecha[hoy];
      const ventaAyer = ventasPorFecha[ayer];
      const diferencia = ventaHoy - ventaAyer;

      if (diferencia > 0) {
        alertaTexto = `🟢 El ${formatearFecha(hoy)} vendiste MÁS que el ${formatearFecha(ayer)} (+$${diferencia.toLocaleString("es-AR")})`;
      } else if (diferencia < 0) {
        alertaTexto = `🔴 El ${formatearFecha(hoy)} vendiste MENOS que el ${formatearFecha(ayer)} (-$${Math.abs(diferencia).toLocaleString("es-AR")})`;
      } else {
        alertaTexto = `⚖️ El ${formatearFecha(hoy)} vendiste lo mismo que el ${formatearFecha(ayer)}`;
      }
    }

    document.getElementById("alertaVentas").textContent = alertaTexto;

    const ventasPorDiaSemana = {};
    const diasSemana = [
      "Domingo",
      "Lunes",
      "Martes",
      "Miércoles",
      "Jueves",
      "Viernes",
      "Sábado",
    ];

    data.forEach((p) => {
      if (p.estado === "pagado") {
        const [anio, mes, dia] = p.fecha.split("-").map(Number);
        const fechaObj = new Date(anio, mes - 1, dia);
        const diaSemana = diasSemana[fechaObj.getDay()];

        if (!ventasPorDiaSemana[diaSemana]) {
          ventasPorDiaSemana[diaSemana] = 0;
        }

        ventasPorDiaSemana[diaSemana] += Number(p.monto);
      }
    });

    let mejorDiaSemana = null;
    let peorDiaSemana = null;
    let maxDiaSemana = -Infinity;
    let minDiaSemana = Infinity;

    for (const dia in ventasPorDiaSemana) {
      const venta = ventasPorDiaSemana[dia];

      if (venta > maxDiaSemana) {
        maxDiaSemana = venta;
        mejorDiaSemana = dia;
      }

      if (venta < minDiaSemana) {
        minDiaSemana = venta;
        peorDiaSemana = dia;
      }
    }

    document.getElementById("mejorDiaSemana").textContent =
      mejorDiaSemana ? `${mejorDiaSemana} ($${maxDiaSemana.toLocaleString("es-AR")})` : "-";

    document.getElementById("peorDiaSemana").textContent =
      peorDiaSemana ? `${peorDiaSemana} ($${minDiaSemana.toLocaleString("es-AR")})` : "-";

    renderGraficoVentas(data);

    data.forEach((p) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${p.id}</td>
        <td>$${Number(p.monto).toLocaleString("es-AR")}</td>
        <td><span class="badge ${p.estado}">${p.estado}</span></td>
        <td>${formatearFecha(p.fecha)}</td>
      `;
      tabla.appendChild(tr);
    });
  } catch (error) {
    console.error("Error en listarPagos:", error);
  }
}

/* =========================
   EXPORTAR EXCEL
========================= */

function descargarCSV() {
  if (!datosActuales || datosActuales.length === 0) {
    alert("No hay datos para exportar");
    return;
  }

  const datosParaExcel = datosActuales.map((p) => ({
    ID: p.id,
    Monto: Number(p.monto),
    Estado: p.estado,
    Fecha: formatearFecha(p.fecha),
  }));

  const worksheet = XLSX.utils.json_to_sheet(datosParaExcel);

  worksheet["!cols"] = [
    { wch: 10 },
    { wch: 15 },
    { wch: 15 },
    { wch: 25 },
  ];

  const rango = XLSX.utils.decode_range(worksheet["!ref"]);
  for (let fila = rango.s.r + 1; fila <= rango.e.r; fila++) {
    const celdaMonto = XLSX.utils.encode_cell({ r: fila, c: 1 });
    if (worksheet[celdaMonto]) {
      worksheet[celdaMonto].z = '$ #,##0';
    }
  }

  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "Pagos");

  const hoy = new Date();
  const fechaArchivo = hoy.toISOString().slice(0, 10);

  XLSX.writeFile(workbook, `reporte_pagos_${fechaArchivo}.xlsx`);
}

/* =========================
   INIT
========================= */

window.onload = function () {
  prepararValidacionAuth();
  configurarEnterAuth();

  if (getAccessToken()) {
    verMiSesion()
      .then(() => listarPagos().catch(() => {}))
      .catch(() => {
        limpiarTokens();
        limpiarCamposAuth();
        ocultarSesion();
      });
  } else {
    ocultarSesion();
  }
};

function configurarEnterAuth() {
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Enter") return;

    const campoActivo = document.activeElement.id;

    const camposLogin = ["loginEmail", "loginPassword"];
    const camposRegistro = [
      "registroNombre",
      "registroEmail",
      "registroPassword",
      "registroComercioId"
    ];

    let boton = null;

    if (camposLogin.includes(campoActivo)) {
      boton = document.getElementById("btnLogin");
    }

    if (camposRegistro.includes(campoActivo)) {
      boton = document.getElementById("btnRegistro");
    }

    if (!boton) return;

    e.preventDefault();

    boton.classList.add("enter-pressed");

    setTimeout(() => {
      boton.classList.remove("enter-pressed");
      boton.click();
    }, 120);
  });
}

function mostrarSesion(usuario) {
  const contenedor = document.getElementById("sesionInfo");
  const texto = document.getElementById("usuarioLogueado");
  const authCard = document.getElementById("authCard");
  const appContent = document.getElementById("appContent");

  texto.textContent = `Logueado como: ${usuario.nombre} (${usuario.email})`;

  contenedor.style.display = "flex";
  authCard.style.display = "none";
  appContent.style.display = "block";
}

function ocultarSesion() {
  const contenedor = document.getElementById("sesionInfo");
  const authCard = document.getElementById("authCard");
  const appContent = document.getElementById("appContent");

  contenedor.style.display = "none";
  authCard.style.display = "block";
  appContent.style.display = "none";
}

function setError(id, mensaje) {
  document.getElementById(id).textContent = mensaje;
}

function limpiarErroresAuth() {
  setError("errorLoginEmail", "");
  setError("errorLoginPassword", "");
  setError("errorRegistroNombre", "");
  setError("errorRegistroEmail", "");
  setError("errorRegistroPassword", "");
  setError("errorRegistroNombreComercio", "");
}

function camposLoginCompletos() {
  return (
    document.getElementById("loginEmail").value.trim() &&
    document.getElementById("loginPassword").value.trim()
  );
}

function camposRegistroCompletos() {
  return (
    document.getElementById("registroNombre").value.trim() &&
    document.getElementById("registroEmail").value.trim() &&
    document.getElementById("registroPassword").value.trim() &&
    document.getElementById("registroNombreComercio").value.trim()
  );
}

function actualizarBotonesAuth() {
  const btnLogin = document.getElementById("btnLogin");
  const btnRegistro = document.getElementById("btnRegistro");

  btnLogin.classList.toggle("ready", Boolean(camposLoginCompletos()));
  btnRegistro.classList.toggle("ready", Boolean(camposRegistroCompletos()));
}

function validarLoginVisual() {
  limpiarErroresAuth();

  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value.trim();

  let valido = true;

  if (!email) {
    setError("errorLoginEmail", "Ingresá tu email.");
    valido = false;
  }
  else if (!esEmailValido(email)) {
    setError("errorLoginEmail", "Ingresá un email válido.");
    valido = false;
  }

  if (!password) {
    setError("errorLoginPassword", "Ingresá tu contraseña.");
    valido = false;
  }

  return valido;
}

function validarRegistroVisual() {
  limpiarErroresAuth();

  const nombre = document.getElementById("registroNombre").value.trim();
  const email = document.getElementById("registroEmail").value.trim();
  const password = document.getElementById("registroPassword").value.trim();
  const nombreComercio = document.getElementById("registroNombreComercio").value.trim();

  let valido = true;

  if (!nombre) {
    setError("errorRegistroNombre", "Ingresá tu nombre.");
    valido = false;
  }

  if (!email) {
    setError("errorRegistroEmail", "Ingresá tu email.");
    valido = false;
  }
  else if (!esEmailValido(email)) {
    setError("errorRegistroEmail", "Ingresá un email válido.");
    valido = false;
  }

  if (!password) {
    setError("errorRegistroPassword", "Ingresá una contraseña.");
    valido = false;
  }

  if (!nombreComercio) {
    setError("errorRegistroNombreComercio", "Ingresá el nombre del comercio.");
  }

  return valido;
}

function prepararValidacionAuth() {
  const campos = [
    "loginEmail",
    "loginPassword",
    "registroNombre",
    "registroEmail",
    "registroPassword",
    "registroNombreComercio",
  ];

  campos.forEach((id) => {
    document.getElementById(id).addEventListener("input", actualizarBotonesAuth);
  });

  actualizarBotonesAuth();
}

function limpiarCamposAuth() {
  // login
  document.getElementById("loginEmail").value = "";
  document.getElementById("loginPassword").value = "";

  // registro
  document.getElementById("registroNombre").value = "";
  document.getElementById("registroEmail").value = "";
  document.getElementById("registroPassword").value = "";
  document.getElementById("registroNombreComercio").value = "";

  // limpiar errores visuales
  limpiarErroresAuth();

  // resetear botones
  actualizarBotonesAuth();
}

function mostrarRegistroMensaje(mensaje, esError = false) {
  const registroResultado = document.getElementById("registroResultado");
  registroResultado.innerHTML = `<p style="color:${esError ? "red" : "green"};">${mensaje}</p>`;
}

function esEmailValido(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}