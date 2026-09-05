/**
 * Myntra Sense — Master 4-Screen Router & Application Coordinator
 */

class AppRouter {
  constructor() {
    this.currentScreen = "HOME";
    this.screens = {
      HOME: document.getElementById("screen-home"),
      PDP: document.getElementById("screen-pdp"),
      CHECKOUT: document.getElementById("screen-checkout"),
      WISHLIST: document.getElementById("screen-wishlist")
    };
  }

  navigateTo(screenName) {
    this.currentScreen = screenName;
    window.scrollTo({ top: 0, behavior: "smooth" });

    // Hide all screens, show active screen
    Object.keys(this.screens).forEach(key => {
      const el = this.screens[key];
      if (el) {
        if (key === screenName) {
          el.classList.add("active-screen");
        } else {
          el.classList.remove("active-screen");
        }
      }
    });

    // Update navigation pills
    const pills = document.querySelectorAll(".screen-nav-pill");
    pills.forEach(p => {
      if (p.getAttribute("data-screen") === screenName) {
        p.classList.add("active");
      } else {
        p.classList.remove("active");
      }
    });

    // Lifecycle triggers
    if (screenName === "CHECKOUT") {
      window.checkoutSense.render();
    } else if (screenName === "WISHLIST") {
      window.wishlistCompare.render();
    }
  }

  navigateToPDP(productId) {
    this.navigateTo("PDP");
    window.sensePDP.renderProduct(productId);
  }
}

window.appRouter = new AppRouter();

document.addEventListener("DOMContentLoaded", async () => {
  console.log("🚀 Initializing Myntra Sense 4-Screen Application...");

  // Initial Load of Home Picks
  const initialData = await window.senseAPI.getHomePicks("USR_10001");
  window.senseHome.render(initialData);

  // Setup Persona Switcher
  const personaSelect = document.getElementById("persona-select-dropdown");
  if (personaSelect) {
    personaSelect.addEventListener("change", async (e) => {
      const val = e.target.value;
      const refreshedData = await window.senseAPI.getHomePicks(val);
      window.senseHome.render(refreshedData);
      if (window.appRouter.currentScreen === "WISHLIST") {
        window.wishlistCompare.render();
      }
    });
  }

  // Setup Search Bar
  const searchInput = document.getElementById("nav-search-input");
  if (searchInput) {
    searchInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        window.appRouter.navigateTo("HOME");
        const banner = document.getElementById("sense-hero-banner");
        if (banner) banner.scrollIntoView({ behavior: "smooth" });
      }
    });
  }

  // Escape key closes comparison modal
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      window.wishlistCompare.closeModal();
    }
  });

  console.log("✅ Myntra Sense 4-Screen App Ready!");
});
