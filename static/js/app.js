(function () {
  "use strict";

  const API = "/api/v1/restaurants";

  function showMessage(text, kind) {
    const el = document.getElementById("message");
    if (!el) return;
    el.textContent = text;
    el.className = "message " + (kind || "");
  }

  // Convierte la respuesta de error de la API (string o lista de errores 422) en texto legible.
  async function errorText(response) {
    try {
      const payload = await response.json();
      const detail = payload.detail;
      if (typeof detail === "string") return detail;
      if (Array.isArray(detail)) {
        return detail
          .map((e) => {
            const field = e.loc && e.loc.length ? e.loc[e.loc.length - 1] : "";
            return field && field !== "body" ? field + ": " + e.msg : e.msg;
          })
          .join(" · ");
      }
    } catch (_) {
      /* respuesta sin JSON */
    }
    return "Error al guardar (código " + response.status + ")";
  }

  // --- Crear / editar ---
  const form = document.getElementById("restaurant-form");
  if (form) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const button = form.querySelector("button[type=submit]");
      const isEdit = form.dataset.mode === "edit";

      const data = Object.fromEntries(new FormData(form));
      data.price = Number(data.price);

      const url = isEdit ? API + "/" + form.dataset.id : API;
      button.disabled = true;
      showMessage("Guardando…", "");

      try {
        const response = await fetch(url, {
          method: isEdit ? "PATCH" : "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });

        if (response.ok) {
          const saved = await response.json();
          showMessage(
            isEdit ? "Restaurante actualizado correctamente" : "Restaurante creado correctamente",
            "success"
          );
          setTimeout(() => {
            window.location.href = "/restaurants/" + saved.id;
          }, 800);
          return;
        }
        showMessage(await errorText(response), "error");
      } catch (_) {
        showMessage("No se pudo conectar con el servidor", "error");
      }
      button.disabled = false;
    });
  }

  // --- Eliminar ---
  document.querySelectorAll("[data-delete]").forEach((button) => {
    button.addEventListener("click", async () => {
      const name = button.dataset.name || "este restaurante";
      if (!window.confirm('¿Eliminar "' + name + '"? Esta acción no se puede deshacer.')) {
        return;
      }
      button.disabled = true;
      try {
        const response = await fetch(API + "/" + button.dataset.id, { method: "DELETE" });
        if (response.status === 204) {
          window.location.href = "/?deleted=1"; // el listado se vuelve a cargar sin el restaurante
          return;
        }
        showMessage(await errorText(response), "error");
      } catch (_) {
        showMessage("No se pudo conectar con el servidor", "error");
      }
      button.disabled = false;
    });
  });
})();
