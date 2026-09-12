const API_URL = window.GCHY_API_URL || window.localStorage.getItem("gchy_api_url") || "http://localhost:8000";
const ADMIN_TOKEN_KEY = "gchy_admin_token";
const ADMIN_USERNAME_KEY = "gchy_admin_username";
const state = { menu: [], cart: [], filter: "all" };
const adminState = { token: localStorage.getItem(ADMIN_TOKEN_KEY) || "", username: localStorage.getItem(ADMIN_USERNAME_KEY) || "", editingId: null };
const $ = (selector) => document.querySelector(selector);
const money = (value) => `Rs ${Number(value).toFixed(2)}`;
const icons = ["●", "◆", "✦", "●", "◆", "✦"];

async function request(path, options = {}, token = null) {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Something went wrong. Please try again.");
  }
  return response.status === 204 ? null : response.json();
}

function renderMenu() {
  const visible = state.menu.filter((item) => item.is_available && (state.filter === "all" || item.category === state.filter));
  $("#menu-grid").innerHTML = visible.length ? visible.map((item, index) => `<article class="menu-card"><div class="menu-icon">${icons[index % icons.length]}</div><span class="menu-category">${escapeHtml(item.category)}</span><h3>${escapeHtml(item.name)}</h3><p>${escapeHtml(item.description || "A Chaat Corner favourite.")}</p><div class="card-bottom"><span class="price">${money(item.price)}</span><button class="add-button" data-add="${item.id}" aria-label="Add ${escapeHtml(item.name)} to cart">+</button></div></article>`).join("") : `<p class="loading">No items in this category yet.</p>`;
}

function renderCart() {
  const count = state.cart.reduce((sum, item) => sum + item.quantity, 0);
  const total = state.cart.reduce((sum, item) => sum + item.quantity * Number(item.price), 0);
  $("#cart-count").textContent = count;
  $("#cart-total").textContent = money(total);
  $("#cart-items").innerHTML = state.cart.length ? state.cart.map((item) => `<div class="cart-line"><div><h4>${escapeHtml(item.name)}</h4><small>${money(item.price)} each</small></div><div class="quantity"><button data-decrease="${item.id}" aria-label="Decrease quantity">-</button><span>${item.quantity}</span><button data-increase="${item.id}" aria-label="Increase quantity">+</button></div></div>`).join("") : `<p class="empty-cart">Your cart is waiting for something delicious.</p>`;
}

function addToCart(id) {
  const item = state.menu.find((entry) => entry.id === id);
  if (!item) return;
  const existing = state.cart.find((entry) => entry.id === id);
  existing ? existing.quantity += 1 : state.cart.push({ ...item, quantity: 1 });
  renderCart();
  showToast(`${item.name} added to your order`);
}

function changeQuantity(id, delta) {
  const item = state.cart.find((entry) => entry.id === id);
  if (!item) return;
  item.quantity += delta;
  if (item.quantity <= 0) state.cart = state.cart.filter((entry) => entry.id !== id);
  renderCart();
}

function toggleCart(open) {
  $("#cart-drawer").classList.toggle("open", open);
  $("#overlay").classList.toggle("visible", open);
  $("#cart-drawer").setAttribute("aria-hidden", String(!open));
}

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2600);
}

function showAdminStatus(message, isError = false) {
  const status = $("#admin-status");
  if (!status) return;
  status.textContent = message;
  status.style.color = isError ? "#d94d2b" : "#2b6c53";
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[char]));
}

function setAdminSession(token, username) {
  adminState.token = token;
  adminState.username = username;
  localStorage.setItem(ADMIN_TOKEN_KEY, token);
  localStorage.setItem(ADMIN_USERNAME_KEY, username);
  updateAdminAuthView();
}

function clearAdminSession() {
  adminState.token = "";
  adminState.username = "";
  adminState.editingId = null;
  localStorage.removeItem(ADMIN_TOKEN_KEY);
  localStorage.removeItem(ADMIN_USERNAME_KEY);
  updateAdminAuthView();
  resetMenuForm();
}

function updateAdminAuthView() {
  const isLoggedIn = Boolean(adminState.token);
  $("#admin-login-card").hidden = isLoggedIn;
  $("#admin-authenticated").hidden = !isLoggedIn;
  $("#admin-username-display").textContent = isLoggedIn ? adminState.username : "Admin";
}

function resetMenuForm() {
  adminState.editingId = null;
  $("#menu-item-id").value = "";
  $("#menu-name").value = "";
  $("#menu-category").value = "snacks";
  $("#menu-description").value = "";
  $("#menu-price").value = "";
  $("#menu-available").checked = true;
  $("#save-menu-item").textContent = "Save item";
  $("#cancel-menu-edit").style.display = "none";
}

async function adminRequest(path, options = {}) {
  if (!adminState.token) {
    throw new Error("Admin session expired. Please log in again.");
  }

  try {
    return await request(path, options, adminState.token);
  } catch (error) {
    const message = String(error.message || "").toLowerCase();
    if (message.includes("unauthorized") || message.includes("expired") || message.includes("token")) {
      clearAdminSession();
      showAdminStatus("Your session has expired. Please log in again.", true);
    }
    throw error;
  }
}

function renderAdminMenuList() {
  const adminList = $("#admin-menu-list");
  if (!adminList) return;

  if (!state.menu.length) {
    adminList.innerHTML = '<div class="empty-admin-list">No menu items yet. Add one to start selling.</div>';
    return;
  }

  adminList.innerHTML = state.menu.map((item) => `
    <article class="admin-item">
      <div class="admin-item-copy">
        <span class="admin-item-badge ${item.is_available ? "available" : "hidden"}">${item.is_available ? "Available" : "Hidden"}</span>
        <h4>${escapeHtml(item.name)}</h4>
        <p>${escapeHtml(item.description || "No description provided.")}</p>
      </div>
      <div class="admin-item-meta">
        <strong>${money(item.price)}</strong>
        <div class="admin-item-actions">
          <button type="button" class="button button-secondary small admin-mini-button" data-edit-item="${item.id}">Edit</button>
          <button type="button" class="button button-danger small admin-mini-button" data-delete-item="${item.id}">Delete</button>
        </div>
      </div>
    </article>
  `).join("");
}

async function loadAdminMenu() {
  if (!adminState.token) {
    renderAdminMenuList();
    return;
  }

  try {
    const items = await adminRequest("/api/menu");
    state.menu = items;
    renderMenu();
    renderAdminMenuList();
  } catch (error) {
    showAdminStatus(error.message, true);
  }
}

async function loadMenu() {
  try {
    state.menu = await request("/api/menu");
    renderMenu();
    renderAdminMenuList();
  } catch (error) {
    $("#menu-grid").innerHTML = `<p class="loading">${escapeHtml(error.message)} Check that the API is running.</p>`;
  }
}

$("#menu-grid").addEventListener("click", (event) => {
  const button = event.target.closest("[data-add]");
  if (button) addToCart(Number(button.dataset.add));
});

document.querySelector(".category-tabs").addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) return;
  document.querySelectorAll(".category-tabs button").forEach((tab) => tab.classList.remove("active"));
  button.classList.add("active");
  state.filter = button.dataset.filter;
  renderMenu();
});

$("#cart-items").addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) return;
  changeQuantity(Number(button.dataset.increase || button.dataset.decrease), button.dataset.increase ? 1 : -1);
});

$("#cart-button").addEventListener("click", () => toggleCart(true));
$("#close-cart").addEventListener("click", () => toggleCart(false));
$("#overlay").addEventListener("click", () => toggleCart(false));

$("#checkout-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const status = $("#checkout-status");
  if (!state.cart.length) {
    status.textContent = "Add at least one item first.";
    return;
  }
  const form = new FormData(event.target);
  const payload = {
    customer_name: form.get("customer_name"),
    customer_phone: form.get("customer_phone"),
    items: state.cart.map((item) => ({ menu_item_id: item.id, quantity: item.quantity })),
  };
  status.textContent = "Sending your order...";
  try {
    const order = await request("/api/orders", { method: "POST", body: JSON.stringify(payload) });
    state.cart = [];
    renderCart();
    event.target.reset();
    status.textContent = "";
    showToast(`Order #${order.id} received. Thank you!`);
  } catch (error) {
    status.textContent = error.message;
  }
});

$("#contact-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const status = $("#contact-status");
  const form = new FormData(event.target);
  status.textContent = "Sending...";
  try {
    await request("/api/contact", { method: "POST", body: JSON.stringify(Object.fromEntries(form)) });
    event.target.reset();
    status.textContent = "Thanks - we will be in touch soon.";
  } catch (error) {
    status.textContent = error.message;
  }
});

$("#admin-login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  const username = String(form.get("username") || "").trim();
  const password = String(form.get("password") || "").trim();

  if (!username || !password) {
    showAdminStatus("Please enter both username and password.", true);
    return;
  }

  try {
    const tokenResponse = await request("/api/admin/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    setAdminSession(tokenResponse.access_token, username);
    event.target.reset();
    showAdminStatus(`Signed in as ${username}.`);
    await loadAdminMenu();
  } catch (error) {
    showAdminStatus(error.message, true);
  }
});

$("#admin-menu-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  const payload = {
    name: String(form.get("name") || "").trim(),
    category: String(form.get("category") || "snacks"),
    description: String(form.get("description") || "").trim() || null,
    price: Number(form.get("price")),
    is_available: form.get("is_available") === "on",
  };

  if (!payload.name || !Number.isFinite(payload.price) || payload.price <= 0) {
    showAdminStatus("Please enter a valid menu item name and price.", true);
    return;
  }

  const isEditing = Boolean(adminState.editingId);

  try {
    if (isEditing) {
      await adminRequest(`/api/menu/${adminState.editingId}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
      showAdminStatus("Menu item updated successfully.");
    } else {
      await adminRequest("/api/menu", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      showAdminStatus("Menu item created successfully.");
    }

    resetMenuForm();
    await loadMenu();
    await loadAdminMenu();
    showToast(isEditing ? "Menu item updated." : "Menu item added.");
  } catch (error) {
    showAdminStatus(error.message, true);
  }
});

$("#admin-menu-list").addEventListener("click", async (event) => {
  const editButton = event.target.closest("[data-edit-item]");
  if (editButton) {
    const item = state.menu.find((entry) => entry.id === Number(editButton.dataset.editItem));
    if (!item) return;

    adminState.editingId = item.id;
    $("#menu-name").value = item.name;
    $("#menu-category").value = item.category;
    $("#menu-description").value = item.description || "";
    $("#menu-price").value = Number(item.price).toFixed(2);
    $("#menu-available").checked = Boolean(item.is_available);
    $("#save-menu-item").textContent = "Update item";
    $("#cancel-menu-edit").style.display = "inline-flex";
    $("#menu-name").focus();
    showAdminStatus(`Editing ${item.name}.`);
    return;
  }

  const deleteButton = event.target.closest("[data-delete-item]");
  if (!deleteButton) return;

  const itemId = Number(deleteButton.dataset.deleteItem);
  const item = state.menu.find((entry) => entry.id === itemId);
  if (!item) return;

  const confirmed = window.confirm(`Delete ${item.name}?`);
  if (!confirmed) return;

  try {
    await adminRequest(`/api/menu/${itemId}`, { method: "DELETE" });
    showAdminStatus(`${item.name} removed.`);
    await loadMenu();
    await loadAdminMenu();
    showToast(`${item.name} deleted.`);
  } catch (error) {
    showAdminStatus(error.message, true);
  }
});

$("#admin-logout").addEventListener("click", () => {
  clearAdminSession();
  showAdminStatus("Signed out.");
});

$("#refresh-admin-menu").addEventListener("click", () => {
  loadAdminMenu();
});

$("#cancel-menu-edit").addEventListener("click", () => {
  resetMenuForm();
  showAdminStatus("Edit cancelled.");
});

$("#admin-portal-toggle").addEventListener("click", () => {
  const adminShell = $("#admin");
  const panel = $("#admin-panel");
  const isOpen = adminShell.hidden;
  adminShell.hidden = !isOpen;
  panel.classList.toggle("open", isOpen);
  $("#admin-portal-toggle").textContent = isOpen ? "Close admin" : "Open admin";
  $("#admin-portal-toggle").setAttribute("aria-expanded", String(isOpen));
  if (isOpen) {
    panel.scrollIntoView({ behavior: "smooth", block: "start" });
  }
});

updateAdminAuthView();
renderCart();
loadMenu();
resetMenuForm();
if (adminState.token) {
  showAdminStatus(`Signed in as ${adminState.username}.`);
  loadAdminMenu();
}
