import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "./store/auth";

//INFO: lazy import
const Landing = () => import("./views/Landing.vue");
const Login = () => import("./views/Login.vue");
const Register = () => import("./views/Register.vue");
const AdminDashboard = () => import("./views/admin/AdminDashboard.vue");
const AdminTreks = () => import("./views/admin/AdminTreks.vue");
const AdminUsers = () => import("./views/admin/AdminUsers.vue");
const AdminBookings = () => import("./views/admin/AdminBookings.vue");
const StaffDashboard = () => import("./views/staff/StaffDashboard.vue");
const Participants = () => import("./views/staff/Participants.vue");
const TrekList = () => import("./views/trekker/TrekList.vue");
const MyBookings = () => import("./views/trekker/MyBookings.vue");
const Profile = () => import("./views/trekker/Profile.vue");

const routes = [
  { path: "/login", component: Login },
  { path: "/register", component: Register },
  { path: "/profile", component: Profile, meta: { requiresAuth: true } },
  {
    path: "/admin",
    component: AdminDashboard,
    meta: { requiresAuth: true, role: "admin" },
  },
  {
    path: "/admin/users",
    component: AdminUsers,
    meta: { requiresAuth: true, role: "admin" },
  },
  {
    path: "/staff",
    component: StaffDashboard,
    meta: { requiresAuth: true, role: "staff" },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const auth = useAuthStore();

  if (to.path === "/") {
    return "/login";
  }
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return "/login";
  }

  if (to.meta.role && auth.role !== to.meta.role) {
    if (auth.role === "admin") return "/admin";
    if (auth.role === "staff") return "/staff";
    if (auth.role === "trekker") return "/treks";
    return "/login";
  }

  if (
    (to.path === "/" || to.path === "/login" || to.path === "/register") &&
    auth.isLoggedIn
  ) {
    if (auth.role === "admin") return "/admin";
    if (auth.role === "staff") return "/staff";
    return "/treks";
  }
});

export default router;
