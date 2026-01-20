module.exports = [
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/action-async-storage.external.js [external] (next/dist/server/app-render/action-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/action-async-storage.external.js", () => require("next/dist/server/app-render/action-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-unit-async-storage.external.js [external] (next/dist/server/app-render/work-unit-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-unit-async-storage.external.js", () => require("next/dist/server/app-render/work-unit-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-async-storage.external.js [external] (next/dist/server/app-render/work-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-async-storage.external.js", () => require("next/dist/server/app-render/work-async-storage.external.js"));

module.exports = mod;
}),
"[project]/lib/utils.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "cn",
    ()=>cn
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/clsx/dist/clsx.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$tailwind$2d$merge$2f$dist$2f$bundle$2d$mjs$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/tailwind-merge/dist/bundle-mjs.mjs [app-ssr] (ecmascript)");
;
;
function cn(...inputs) {
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$tailwind$2d$merge$2f$dist$2f$bundle$2d$mjs$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["twMerge"])((0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["clsx"])(inputs));
}
}),
"[project]/contexts/sidebar-context.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "SidebarProvider",
    ()=>SidebarProvider,
    "useSidebar",
    ()=>useSidebar
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
"use client";
;
;
const SidebarContext = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["createContext"])(undefined);
function SidebarProvider({ children }) {
    const [isCollapsed, setIsCollapsed] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [mounted, setMounted] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        const stored = localStorage.getItem("sidebarCollapsed") === "true";
        setIsCollapsed(stored);
        setMounted(true);
    }, []);
    const toggleCollapse = ()=>{
        setIsCollapsed((prev)=>{
            const newState = !prev;
            localStorage.setItem("sidebarCollapsed", String(newState));
            return newState;
        });
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(SidebarContext.Provider, {
        value: {
            isCollapsed,
            toggleCollapse,
            mounted
        },
        children: children
    }, void 0, false, {
        fileName: "[project]/contexts/sidebar-context.tsx",
        lineNumber: 32,
        columnNumber: 10
    }, this);
}
function useSidebar() {
    const context = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useContext"])(SidebarContext);
    if (context === undefined) {
        throw new Error("useSidebar must be used within SidebarProvider");
    }
    return context;
}
}),
"[project]/lib/store/hooks.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Typed Redux hooks
 */ __turbopack_context__.s([
    "useAppDispatch",
    ()=>useAppDispatch,
    "useAppSelector",
    ()=>useAppSelector
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$redux$2f$dist$2f$react$2d$redux$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/react-redux/dist/react-redux.mjs [app-ssr] (ecmascript)");
;
const useAppDispatch = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$redux$2f$dist$2f$react$2d$redux$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useDispatch"].withTypes();
const useAppSelector = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$redux$2f$dist$2f$react$2d$redux$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useSelector"].withTypes();
}),
"[project]/lib/store/slices/permissionSlice.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "PAGE_PERMISSIONS",
    ()=>PAGE_PERMISSIONS,
    "canAccessPage",
    ()=>canAccessPage,
    "clearPermissions",
    ()=>clearPermissions,
    "default",
    ()=>__TURBOPACK__default__export__,
    "hasAllPermissions",
    ()=>hasAllPermissions,
    "hasAnyPermission",
    ()=>hasAnyPermission,
    "hasPermission",
    ()=>hasPermission,
    "setPermissions",
    ()=>setPermissions
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/@reduxjs/toolkit/dist/redux-toolkit.modern.mjs [app-ssr] (ecmascript) <locals>");
;
const initialState = {
    permissions: [],
    isLoading: false,
    error: null
};
const permissionSlice = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createSlice"])({
    name: 'permissions',
    initialState,
    reducers: {
        setPermissions: (state, action)=>{
            state.permissions = action.payload;
        },
        clearPermissions: (state)=>{
            state.permissions = [];
        }
    }
});
const { setPermissions, clearPermissions } = permissionSlice.actions;
const __TURBOPACK__default__export__ = permissionSlice.reducer;
// Permission matrix (matches backend)
const PERMISSION_MATRIX = {
    create_user: [
        'super_admin',
        'org_admin'
    ],
    manage_roles: [
        'super_admin',
        'org_admin'
    ],
    create_connection: [
        'super_admin',
        'org_admin',
        'data_engineer'
    ],
    view_credentials: [],
    test_connection: [
        'super_admin',
        'org_admin',
        'data_engineer'
    ],
    create_pipeline: [
        'super_admin',
        'org_admin',
        'data_engineer'
    ],
    start_stop_pipeline: [
        'super_admin',
        'org_admin',
        'operator'
    ],
    pause_pipeline: [
        'super_admin',
        'org_admin',
        'operator'
    ],
    reset_offsets: [
        'super_admin',
        'org_admin'
    ],
    trigger_full_load: [
        'super_admin',
        'org_admin',
        'data_engineer'
    ],
    delete_pipeline: [
        'super_admin',
        'org_admin'
    ],
    view_metrics: [
        'super_admin',
        'org_admin',
        'data_engineer',
        'operator',
        'viewer'
    ],
    view_audit_logs: [
        'super_admin',
        'org_admin'
    ]
};
const PAGE_PERMISSIONS = {
    '/dashboard': [
        'view_metrics'
    ],
    '/monitoring': [
        'view_metrics'
    ],
    '/connections': [
        'create_connection'
    ],
    '/pipelines': [
        'create_pipeline'
    ],
    '/analytics': [
        'view_metrics'
    ],
    '/errors': [
        'view_metrics'
    ],
    '/governance': [
        'view_metrics'
    ],
    '/users': [
        'create_user'
    ],
    '/settings': [
        'manage_roles'
    ]
};
const hasPermission = (permission)=>(state)=>{
        // Check if user has explicit permission
        if (state.permissions?.permissions?.includes(permission)) {
            return true;
        }
        // Check user role from auth state
        const user = state.auth?.user;
        if (!user) return false;
        // Super admin has all permissions
        if (user.is_superuser || user.role_name === 'super_admin') {
            return true;
        }
        // Check role-based permissions
        const allowedRoles = PERMISSION_MATRIX[permission] || [];
        const userRole = user.role_name?.toLowerCase();
        return allowedRoles.includes(userRole);
    };
const hasAnyPermission = (permissions)=>(state)=>{
        return permissions.some((perm)=>state.permissions.permissions.includes(perm));
    };
const hasAllPermissions = (permissions)=>(state)=>{
        return permissions.every((perm)=>state.permissions.permissions.includes(perm));
    };
const canAccessPage = (path)=>(state)=>{
        const user = state.auth?.user;
        if (!user) return false;
        // Super admin has access to all pages - check multiple ways
        const isSuperAdmin = user.is_superuser === true || user.is_superuser === 'true' || String(user.is_superuser).toLowerCase() === 'true' || user.role_name === 'super_admin' || user.role_name === 'admin';
        if (isSuperAdmin) {
            return true;
        }
        // Dashboard is accessible to all authenticated users
        if (path === '/dashboard') {
            return true;
        }
        // Get required permissions for the page
        const requiredPermissions = PAGE_PERMISSIONS[path] || [];
        // If no permissions required, allow access
        if (requiredPermissions.length === 0) {
            return true;
        }
        // Check if user has any of the required permissions
        return requiredPermissions.some((permission)=>hasPermission(permission)(state));
    };
}),
"[project]/components/layout/sidebar.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "Sidebar",
    ()=>Sidebar
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/client/app-dir/link.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/utils.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$database$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Database$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/database.js [app-ssr] (ecmascript) <export default as Database>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chart$2d$column$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__BarChart3$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chart-column.js [app-ssr] (ecmascript) <export default as BarChart3>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/settings.js [app-ssr] (ecmascript) <export default as Settings>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$branch$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__GitBranch$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/git-branch.js [app-ssr] (ecmascript) <export default as GitBranch>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__AlertTriangle$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/triangle-alert.js [app-ssr] (ecmascript) <export default as AlertTriangle>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$activity$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Activity$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/activity.js [app-ssr] (ecmascript) <export default as Activity>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$house$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Home$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/house.js [app-ssr] (ecmascript) <export default as Home>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$shield$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Shield$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/shield.js [app-ssr] (ecmascript) <export default as Shield>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$users$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Users$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/users.js [app-ssr] (ecmascript) <export default as Users>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$left$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronLeft$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-left.js [app-ssr] (ecmascript) <export default as ChevronLeft>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$right$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronRight$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-right.js [app-ssr] (ecmascript) <export default as ChevronRight>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-down.js [app-ssr] (ecmascript) <export default as ChevronDown>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$up$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronUp$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-up.js [app-ssr] (ecmascript) <export default as ChevronUp>");
var __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$sidebar$2d$context$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/contexts/sidebar-context.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/hooks.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$permissionSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/permissionSlice.ts [app-ssr] (ecmascript)");
"use client";
;
;
;
;
;
;
;
;
;
const menuSections = [
    {
        title: "PLATFORM",
        items: [
            {
                href: "/dashboard",
                label: "Dashboard",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$house$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Home$3e$__["Home"]
            },
            {
                href: "/monitoring",
                label: "Monitoring",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$activity$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Activity$3e$__["Activity"]
            }
        ]
    },
    {
        title: "REPLICATION",
        items: [
            {
                href: "/connections",
                label: "Connections",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$database$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Database$3e$__["Database"]
            },
            {
                href: "/pipelines",
                label: "Pipelines",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$branch$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__GitBranch$3e$__["GitBranch"]
            },
            {
                href: "/analytics",
                label: "Analytics",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chart$2d$column$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__BarChart3$3e$__["BarChart3"]
            }
        ]
    },
    {
        title: "OPERATIONS",
        items: [
            {
                href: "/errors",
                label: "Errors & Alerts",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__AlertTriangle$3e$__["AlertTriangle"]
            },
            {
                href: "/governance",
                label: "Data Governance",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$shield$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Shield$3e$__["Shield"]
            },
            {
                href: "/users",
                label: "User Management",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$users$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Users$3e$__["Users"]
            },
            {
                href: "/settings",
                label: "Settings",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__["Settings"]
            }
        ]
    }
];
function Sidebar() {
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["usePathname"])();
    const { isCollapsed, toggleCollapse, mounted } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$sidebar$2d$context$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useSidebar"])();
    // Use specific selectors instead of root state to prevent unnecessary rerenders
    const { user, isAuthenticated } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAppSelector"])((state)=>state.auth);
    const permissions = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAppSelector"])((state)=>state.permissions);
    const [expandedSections, setExpandedSections] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])({
        PLATFORM: true,
        REPLICATION: true,
        OPERATIONS: true
    });
    // Filter menu items based on permissions
    const getFilteredMenuSections = ()=>{
        // If user is not loaded yet, show all items (will be filtered once user loads)
        if (!user || !isAuthenticated) {
            return menuSections;
        }
        // Super admin bypass - show all menu items for super admin
        const isSuperAdmin = user.is_superuser === true || user.role_name === 'super_admin' || user.role_name === 'admin' || user.is_superuser === 'true' || // Handle string 'true'
        String(user.is_superuser).toLowerCase() === 'true';
        if (isSuperAdmin) {
            return menuSections;
        }
        // Create minimal state object for permission checks
        const minimalState = {
            auth: {
                user,
                isAuthenticated
            },
            permissions
        };
        return menuSections.map((section)=>({
                ...section,
                items: section.items.filter((item)=>{
                    // Check if user can access this page
                    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$permissionSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["canAccessPage"])(item.href)(minimalState);
                })
            })).filter((section)=>section.items.length > 0) // Remove empty sections
        ;
    };
    // Auto-expand section if current path matches any item in that section
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        if (!isCollapsed) {
            const newExpanded = {};
            menuSections.forEach((section)=>{
                const hasActiveItem = section.items.some((item)=>pathname === item.href || pathname.startsWith(item.href + "/"));
                newExpanded[section.title] = hasActiveItem || expandedSections[section.title];
            });
            setExpandedSections(newExpanded);
        }
    }, [
        pathname,
        isCollapsed
    ]);
    const toggleSection = (sectionTitle)=>{
        if (isCollapsed) return;
        setExpandedSections((prev)=>({
                ...prev,
                [sectionTitle]: !prev[sectionTitle]
            }));
    };
    // Show loading state if not mounted
    if (!mounted) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("aside", {
            className: "w-64 border-r border-border bg-sidebar flex flex-col transition-all duration-300",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "p-6 border-b border-border"
            }, void 0, false, {
                fileName: "[project]/components/layout/sidebar.tsx",
                lineNumber: 121,
                columnNumber: 9
            }, this)
        }, void 0, false, {
            fileName: "[project]/components/layout/sidebar.tsx",
            lineNumber: 120,
            columnNumber: 7
        }, this);
    }
    // Debug: Log user info for super admin check
    if (("TURBOPACK compile-time value", "development") === 'development' && user) {
        console.log('[Sidebar] User check:', {
            is_superuser: user.is_superuser,
            role_name: user.role_name,
            email: user.email,
            willShowAll: user.is_superuser === true || user.role_name === 'super_admin' || user.role_name === 'admin'
        });
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("aside", {
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("border-r border-border bg-sidebar flex flex-col transition-all duration-300", isCollapsed ? "w-20" : "w-64"),
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "p-6 border-b border-border flex items-center justify-between",
                children: [
                    !isCollapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex items-center gap-2",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "w-8 h-8 bg-gradient-to-br from-primary to-info rounded-lg flex items-center justify-center flex-shrink-0",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$database$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Database$3e$__["Database"], {
                                    className: "w-5 h-5 text-foreground"
                                }, void 0, false, {
                                    fileName: "[project]/components/layout/sidebar.tsx",
                                    lineNumber: 148,
                                    columnNumber: 15
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/components/layout/sidebar.tsx",
                                lineNumber: 147,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                                        className: "font-bold text-foreground text-sm",
                                        children: "CDC Admin"
                                    }, void 0, false, {
                                        fileName: "[project]/components/layout/sidebar.tsx",
                                        lineNumber: 151,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        className: "text-xs text-foreground-muted",
                                        children: "Platform"
                                    }, void 0, false, {
                                        fileName: "[project]/components/layout/sidebar.tsx",
                                        lineNumber: 152,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/layout/sidebar.tsx",
                                lineNumber: 150,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/layout/sidebar.tsx",
                        lineNumber: 146,
                        columnNumber: 11
                    }, this),
                    isCollapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "w-8 h-8 bg-gradient-to-br from-primary to-info rounded-lg flex items-center justify-center",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$database$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Database$3e$__["Database"], {
                            className: "w-5 h-5 text-foreground"
                        }, void 0, false, {
                            fileName: "[project]/components/layout/sidebar.tsx",
                            lineNumber: 158,
                            columnNumber: 13
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/layout/sidebar.tsx",
                        lineNumber: 157,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        onClick: toggleCollapse,
                        className: "p-1.5 hover:bg-surface-hover rounded-lg transition-colors",
                        "aria-label": "Toggle sidebar",
                        children: isCollapsed ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$right$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronRight$3e$__["ChevronRight"], {
                            className: "w-4 h-4"
                        }, void 0, false, {
                            fileName: "[project]/components/layout/sidebar.tsx",
                            lineNumber: 166,
                            columnNumber: 26
                        }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$left$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronLeft$3e$__["ChevronLeft"], {
                            className: "w-4 h-4"
                        }, void 0, false, {
                            fileName: "[project]/components/layout/sidebar.tsx",
                            lineNumber: 166,
                            columnNumber: 65
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/layout/sidebar.tsx",
                        lineNumber: 161,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/layout/sidebar.tsx",
                lineNumber: 144,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("nav", {
                className: "flex-1 overflow-y-auto px-3 py-4 space-y-6",
                children: getFilteredMenuSections().map((section)=>{
                    const isExpanded = expandedSections[section.title] ?? true;
                    const hasActiveItem = section.items.some((item)=>pathname === item.href || pathname.startsWith(item.href + "/"));
                    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        children: !isCollapsed ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    onClick: ()=>toggleSection(section.title),
                                    className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold text-foreground-muted uppercase tracking-wider mb-2 transition-colors hover:bg-surface-hover hover:text-primary", hasActiveItem && "text-primary"),
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            children: section.title
                                        }, void 0, false, {
                                            fileName: "[project]/components/layout/sidebar.tsx",
                                            lineNumber: 190,
                                            columnNumber: 21
                                        }, this),
                                        isExpanded ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$up$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronUp$3e$__["ChevronUp"], {
                                            className: "w-3 h-3"
                                        }, void 0, false, {
                                            fileName: "[project]/components/layout/sidebar.tsx",
                                            lineNumber: 192,
                                            columnNumber: 23
                                        }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__["ChevronDown"], {
                                            className: "w-3 h-3"
                                        }, void 0, false, {
                                            fileName: "[project]/components/layout/sidebar.tsx",
                                            lineNumber: 194,
                                            columnNumber: 23
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/layout/sidebar.tsx",
                                    lineNumber: 183,
                                    columnNumber: 19
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("space-y-1 overflow-hidden transition-all duration-300 ease-in-out", isExpanded ? "max-h-96 opacity-100" : "max-h-0 opacity-0"),
                                    children: section.items.map((item)=>{
                                        const Icon = item.icon;
                                        const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
                                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                            href: item.href,
                                            className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors", isActive ? "bg-primary/20 text-primary border border-primary/30 font-semibold" : "text-foreground-muted hover:text-primary hover:bg-surface-hover"),
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(Icon, {
                                                    className: "w-4 h-4 flex-shrink-0"
                                                }, void 0, false, {
                                                    fileName: "[project]/components/layout/sidebar.tsx",
                                                    lineNumber: 219,
                                                    columnNumber: 27
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                    children: item.label
                                                }, void 0, false, {
                                                    fileName: "[project]/components/layout/sidebar.tsx",
                                                    lineNumber: 220,
                                                    columnNumber: 27
                                                }, this)
                                            ]
                                        }, item.href, true, {
                                            fileName: "[project]/components/layout/sidebar.tsx",
                                            lineNumber: 209,
                                            columnNumber: 25
                                        }, this);
                                    })
                                }, void 0, false, {
                                    fileName: "[project]/components/layout/sidebar.tsx",
                                    lineNumber: 199,
                                    columnNumber: 19
                                }, this)
                            ]
                        }, void 0, true) : /* Collapsed Sidebar - Show all items without dropdown */ /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "space-y-1",
                            children: section.items.map((item)=>{
                                const Icon = item.icon;
                                const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
                                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                    href: item.href,
                                    title: item.label,
                                    className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("flex items-center gap-3 py-2 rounded-lg text-sm font-medium transition-colors justify-center px-0", isActive ? "bg-primary/20 text-primary border border-primary/30 font-semibold" : "text-foreground-muted hover:text-primary hover:bg-surface-hover"),
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(Icon, {
                                        className: "w-4 h-4 flex-shrink-0"
                                    }, void 0, false, {
                                        fileName: "[project]/components/layout/sidebar.tsx",
                                        lineNumber: 244,
                                        columnNumber: 25
                                    }, this)
                                }, item.href, false, {
                                    fileName: "[project]/components/layout/sidebar.tsx",
                                    lineNumber: 233,
                                    columnNumber: 23
                                }, this);
                            })
                        }, void 0, false, {
                            fileName: "[project]/components/layout/sidebar.tsx",
                            lineNumber: 228,
                            columnNumber: 17
                        }, this)
                    }, section.title, false, {
                        fileName: "[project]/components/layout/sidebar.tsx",
                        lineNumber: 179,
                        columnNumber: 13
                    }, this);
                })
            }, void 0, false, {
                fileName: "[project]/components/layout/sidebar.tsx",
                lineNumber: 171,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "p-3 border-t border-border",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("glass p-3 rounded-lg text-xs text-foreground-muted", isCollapsed && "flex justify-center"),
                    children: [
                        !isCollapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                    className: "font-semibold mb-1",
                                    children: "v1.0.0"
                                }, void 0, false, {
                                    fileName: "[project]/components/layout/sidebar.tsx",
                                    lineNumber: 260,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                    children: "Real-time CDC Platform"
                                }, void 0, false, {
                                    fileName: "[project]/components/layout/sidebar.tsx",
                                    lineNumber: 261,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true),
                        isCollapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                            className: "font-semibold",
                            children: "v1"
                        }, void 0, false, {
                            fileName: "[project]/components/layout/sidebar.tsx",
                            lineNumber: 264,
                            columnNumber: 27
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/layout/sidebar.tsx",
                    lineNumber: 257,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/components/layout/sidebar.tsx",
                lineNumber: 256,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/layout/sidebar.tsx",
        lineNumber: 137,
        columnNumber: 5
    }, this);
}
}),
"[project]/contexts/theme-context.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ThemeProvider",
    ()=>ThemeProvider,
    "useTheme",
    ()=>useTheme
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
"use client";
;
;
const ThemeContext = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["createContext"])(undefined);
function ThemeProvider({ children }) {
    // Start with "dark" as default to match server-side rendering
    // This prevents hydration mismatch
    const [theme, setTheme] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])("dark");
    const [mounted, setMounted] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        // Mark as mounted to prevent hydration issues
        setMounted(true);
        // Hydrate theme from localStorage on client mount
        const stored = localStorage.getItem("theme");
        if (stored && (stored === "dark" || stored === "light")) {
            setTheme(stored);
            document.documentElement.classList.toggle("dark", stored === "dark");
            document.documentElement.classList.toggle("light", stored === "light");
        } else {
            // Default to dark - ensure DOM matches
            const defaultTheme = "dark";
            setTheme(defaultTheme);
            localStorage.setItem("theme", defaultTheme);
            document.documentElement.classList.remove("light");
            document.documentElement.classList.add("dark");
        }
    }, []);
    const toggleTheme = ()=>{
        setTheme((prev)=>{
            const newTheme = prev === "dark" ? "light" : "dark";
            localStorage.setItem("theme", newTheme);
            document.documentElement.classList.toggle("dark", newTheme === "dark");
            document.documentElement.classList.toggle("light", newTheme === "light");
            return newTheme;
        });
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(ThemeContext.Provider, {
        value: {
            theme,
            toggleTheme
        },
        children: children
    }, void 0, false, {
        fileName: "[project]/contexts/theme-context.tsx",
        lineNumber: 51,
        columnNumber: 10
    }, this);
}
function useTheme() {
    const context = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useContext"])(ThemeContext);
    if (context === undefined) {
        throw new Error("useTheme must be used within ThemeProvider");
    }
    // Return default theme if not mounted yet to prevent hydration issues
    return {
        theme: context.theme || "dark",
        toggleTheme: context.toggleTheme
    };
}
}),
"[externals]/util [external] (util, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("util", () => require("util"));

module.exports = mod;
}),
"[externals]/stream [external] (stream, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("stream", () => require("stream"));

module.exports = mod;
}),
"[externals]/path [external] (path, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("path", () => require("path"));

module.exports = mod;
}),
"[externals]/http [external] (http, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("http", () => require("http"));

module.exports = mod;
}),
"[externals]/https [external] (https, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("https", () => require("https"));

module.exports = mod;
}),
"[externals]/url [external] (url, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("url", () => require("url"));

module.exports = mod;
}),
"[externals]/fs [external] (fs, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("fs", () => require("fs"));

module.exports = mod;
}),
"[externals]/crypto [external] (crypto, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("crypto", () => require("crypto"));

module.exports = mod;
}),
"[externals]/http2 [external] (http2, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("http2", () => require("http2"));

module.exports = mod;
}),
"[externals]/assert [external] (assert, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("assert", () => require("assert"));

module.exports = mod;
}),
"[externals]/tty [external] (tty, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("tty", () => require("tty"));

module.exports = mod;
}),
"[externals]/zlib [external] (zlib, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("zlib", () => require("zlib"));

module.exports = mod;
}),
"[externals]/events [external] (events, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("events", () => require("events"));

module.exports = mod;
}),
"[project]/lib/api/client.ts [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {

const e = new Error("Could not parse module '[project]/lib/api/client.ts'\n\nExpected '=>', got '('");
e.code = 'MODULE_UNPARSABLE';
throw e;
}),
"[project]/lib/store/slices/authSlice.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Auth Redux slice
 */ __turbopack_context__.s([
    "clearError",
    ()=>clearError,
    "createUser",
    ()=>createUser,
    "default",
    ()=>__TURBOPACK__default__export__,
    "getCurrentUser",
    ()=>getCurrentUser,
    "login",
    ()=>login,
    "logout",
    ()=>logout
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/@reduxjs/toolkit/dist/redux-toolkit.modern.mjs [app-ssr] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api/client.ts [app-ssr] (ecmascript)");
;
;
// Helper to safely get from localStorage
const getInitialToken = ()=>{
    if ("TURBOPACK compile-time truthy", 1) return null;
    //TURBOPACK unreachable
    ;
};
// Helper to safely get user from localStorage
const getInitialUser = ()=>{
    if ("TURBOPACK compile-time truthy", 1) return null;
    //TURBOPACK unreachable
    ;
};
const initialState = {
    user: getInitialUser(),
    token: getInitialToken(),
    isAuthenticated: !!getInitialToken(),
    isLoading: false,
    error: null
};
const login = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('auth/login', async ({ email, password }, { rejectWithValue })=>{
    try {
        // Step 1: Login and get token
        const data = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].login(email, password);
        if (!data.access_token) {
            return rejectWithValue('No access token received from server');
        }
        // Step 2: Set token in API client and localStorage
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].setToken(data.access_token);
        // Step 3: Use user from login response (it already has all the data we need)
        // The login response includes the user object with is_superuser and role_name
        // IMPORTANT: Always use the user from login response, don't call getCurrentUser()
        if (data.user) {
            // Normalize user data - ensure is_superuser is boolean
            const user = {
                ...data.user
            }; // Create a copy to avoid mutating the original
            // Ensure is_superuser is a boolean
            if (typeof user.is_superuser !== 'boolean') {
                // Infer from role_name if available
                user.is_superuser = user.role_name === 'super_admin' || user.role_name === 'admin' || user.is_superuser === true || user.is_superuser === 'true' || String(user.is_superuser).toLowerCase() === 'true' || false;
            }
            // Ensure role_name is set
            if (!user.role_name && user.is_superuser) {
                user.role_name = 'super_admin';
            }
            console.log('[Auth] Login response user (BEFORE normalization):', data.user);
            console.log('[Auth] Login response user (AFTER normalization):', {
                email: user.email,
                is_superuser: user.is_superuser,
                role_name: user.role_name,
                full_user: user
            });
            return {
                token: data.access_token,
                user
            };
        }
        // This should never happen if backend is working correctly
        console.error('[Auth] Login response missing user object!', data);
        throw new Error('Login response missing user object');
    } catch (error) {
        const errorMessage = error.response?.data?.detail || error.message || 'Login failed';
        return rejectWithValue(errorMessage);
    }
});
const logout = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('auth/logout', async ()=>{
    await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].logout();
});
const getCurrentUser = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('auth/getCurrentUser', async (_, { rejectWithValue })=>{
    try {
        const user = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].getCurrentUser();
        console.log('[Auth] getCurrentUser RAW response:', user);
        // Normalize user data - ensure is_superuser is boolean
        if (user) {
            // Ensure is_superuser is a boolean
            if (typeof user.is_superuser !== 'boolean') {
                // Infer from role_name if available
                user.is_superuser = user.role_name === 'super_admin' || user.role_name === 'admin' || user.is_superuser === true || user.is_superuser === 'true' || String(user.is_superuser).toLowerCase() === 'true' || false;
            }
            // Ensure role_name is set
            if (!user.role_name && user.is_superuser) {
                user.role_name = 'super_admin';
            }
            console.log('[Auth] getCurrentUser NORMALIZED response:', {
                email: user.email,
                is_superuser: user.is_superuser,
                role_name: user.role_name,
                full_user: user
            });
        }
        if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
        ;
        return user;
    } catch (error) {
        console.error('[Auth] Failed to fetch current user:', error);
        // Don't clear auth state on error - keep cached user if available
        // Only clear if it's an authentication error
        const isAuthError = error?.response?.status === 401 || error?.response?.status === 403;
        if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
        ;
        return rejectWithValue(error.response?.data?.detail || 'Failed to fetch user info');
    }
});
const createUser = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('auth/createUser', async (userData, { rejectWithValue })=>{
    try {
        const user = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].createUser(userData);
        return user;
    } catch (error) {
        return rejectWithValue(error.response?.data?.detail || 'Failed to create account');
    }
});
const authSlice = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createSlice"])({
    name: 'auth',
    initialState,
    reducers: {
        clearError: (state)=>{
            state.error = null;
        }
    },
    extraReducers: (builder)=>{
        builder// Login
        .addCase(login.pending, (state)=>{
            state.isLoading = true;
            state.error = null;
        }).addCase(login.fulfilled, (state, action)=>{
            state.isLoading = false;
            state.token = action.payload.token;
            // Normalize user data - ensure is_superuser is boolean
            const user = action.payload.user;
            if (user) {
                // Ensure is_superuser is a boolean
                if (typeof user.is_superuser !== 'boolean') {
                    // Infer from role_name if available
                    user.is_superuser = user.role_name === 'super_admin' || user.role_name === 'admin' || user.is_superuser === true || user.is_superuser === 'true' || false;
                }
                // Ensure role_name is set
                if (!user.role_name && user.is_superuser) {
                    user.role_name = 'super_admin';
                }
                // Log for debugging
                console.log('[Auth] Setting user after login:', {
                    email: user.email,
                    is_superuser: user.is_superuser,
                    role_name: user.role_name,
                    full_user: user
                });
                state.user = user;
            } else {
                state.user = null;
            }
            state.isAuthenticated = true;
            state.error = null;
            if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
            ;
        }).addCase(login.rejected, (state, action)=>{
            state.isLoading = false;
            state.error = action.payload;
        })// Logout
        .addCase(logout.fulfilled, (state)=>{
            state.user = null;
            state.token = null;
            state.isAuthenticated = false;
            if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
            ;
        })// Get current user
        .addCase(getCurrentUser.fulfilled, (state, action)=>{
            const userData = action.payload;
            // Ensure is_superuser is properly set
            if (userData && typeof userData.is_superuser === 'boolean') {
                state.user = userData;
            } else {
                // If is_superuser is missing or invalid, set it to false and log warning
                console.warn('[Auth] User data missing is_superuser, setting to false:', userData);
                state.user = userData ? {
                    ...userData,
                    is_superuser: false
                } : null;
            }
            state.isAuthenticated = true;
            if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
            ;
        }).addCase(getCurrentUser.rejected, (state, action)=>{
            // Don't clear user data on error - keep cached user if available
            // Only clear if it's an authentication error
            const error = action.payload;
            const isAuthError = error?.response?.status === 401 || error?.response?.status === 403;
            if (isAuthError) {
                // Authentication error - clear everything
                state.user = null;
                state.isAuthenticated = false;
                state.token = null;
                if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
                ;
            } else {
                // Other errors (network, server) - keep cached user data
                console.warn('[Auth] getCurrentUser failed but keeping cached user data:', error);
            // Don't clear state - keep existing user data
            }
        })// Create user
        .addCase(createUser.pending, (state)=>{
            state.isLoading = true;
            state.error = null;
        }).addCase(createUser.fulfilled, (state)=>{
            state.isLoading = false;
        // User created successfully, redirect to login
        }).addCase(createUser.rejected, (state, action)=>{
            state.isLoading = false;
            state.error = action.payload;
        });
    }
});
const { clearError } = authSlice.actions;
const __TURBOPACK__default__export__ = authSlice.reducer;
}),
"[project]/components/ui/dropdown-menu.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "DropdownMenu",
    ()=>DropdownMenu,
    "DropdownMenuCheckboxItem",
    ()=>DropdownMenuCheckboxItem,
    "DropdownMenuContent",
    ()=>DropdownMenuContent,
    "DropdownMenuGroup",
    ()=>DropdownMenuGroup,
    "DropdownMenuItem",
    ()=>DropdownMenuItem,
    "DropdownMenuLabel",
    ()=>DropdownMenuLabel,
    "DropdownMenuPortal",
    ()=>DropdownMenuPortal,
    "DropdownMenuRadioGroup",
    ()=>DropdownMenuRadioGroup,
    "DropdownMenuRadioItem",
    ()=>DropdownMenuRadioItem,
    "DropdownMenuSeparator",
    ()=>DropdownMenuSeparator,
    "DropdownMenuShortcut",
    ()=>DropdownMenuShortcut,
    "DropdownMenuSub",
    ()=>DropdownMenuSub,
    "DropdownMenuSubContent",
    ()=>DropdownMenuSubContent,
    "DropdownMenuSubTrigger",
    ()=>DropdownMenuSubTrigger,
    "DropdownMenuTrigger",
    ()=>DropdownMenuTrigger
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@radix-ui/react-dropdown-menu/dist/index.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/utils.ts [app-ssr] (ecmascript)");
"use client";
;
;
;
;
const DropdownMenu = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Root"];
const DropdownMenuTrigger = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Trigger"];
const DropdownMenuGroup = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Group"];
const DropdownMenuPortal = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Portal"];
const DropdownMenuSub = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Sub"];
const DropdownMenuRadioGroup = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["RadioGroup"];
const DropdownMenuSubTrigger = /*#__PURE__*/ __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["forwardRef"](({ className, inset, children, ...props }, ref)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["SubTrigger"], {
        ref: ref,
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none focus:bg-surface-hover data-[state=open]:bg-surface-hover", inset && "pl-8", className),
        ...props,
        children: [
            children,
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                className: "ml-auto h-4 w-4",
                children: "›"
            }, void 0, false, {
                fileName: "[project]/components/ui/dropdown-menu.tsx",
                lineNumber: 36,
                columnNumber: 5
            }, ("TURBOPACK compile-time value", void 0))
        ]
    }, void 0, true, {
        fileName: "[project]/components/ui/dropdown-menu.tsx",
        lineNumber: 26,
        columnNumber: 3
    }, ("TURBOPACK compile-time value", void 0)));
DropdownMenuSubTrigger.displayName = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["SubTrigger"].displayName;
const DropdownMenuSubContent = /*#__PURE__*/ __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["forwardRef"](({ className, ...props }, ref)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["SubContent"], {
        ref: ref,
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("z-50 min-w-[8rem] overflow-hidden rounded-md border border-border bg-surface p-1 text-foreground shadow-lg data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2", className),
        ...props
    }, void 0, false, {
        fileName: "[project]/components/ui/dropdown-menu.tsx",
        lineNumber: 45,
        columnNumber: 3
    }, ("TURBOPACK compile-time value", void 0)));
DropdownMenuSubContent.displayName = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["SubContent"].displayName;
const DropdownMenuContent = /*#__PURE__*/ __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["forwardRef"](({ className, sideOffset = 4, ...props }, ref)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Portal"], {
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Content"], {
            ref: ref,
            sideOffset: sideOffset,
            className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("z-50 min-w-[8rem] overflow-hidden rounded-md border border-border bg-surface p-1 text-foreground shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2", className),
            ...props
        }, void 0, false, {
            fileName: "[project]/components/ui/dropdown-menu.tsx",
            lineNumber: 61,
            columnNumber: 5
        }, ("TURBOPACK compile-time value", void 0))
    }, void 0, false, {
        fileName: "[project]/components/ui/dropdown-menu.tsx",
        lineNumber: 60,
        columnNumber: 3
    }, ("TURBOPACK compile-time value", void 0)));
DropdownMenuContent.displayName = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Content"].displayName;
const DropdownMenuItem = /*#__PURE__*/ __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["forwardRef"](({ className, inset, ...props }, ref)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Item"], {
        ref: ref,
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors focus:bg-surface-hover focus:text-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50", inset && "pl-8", className),
        ...props
    }, void 0, false, {
        fileName: "[project]/components/ui/dropdown-menu.tsx",
        lineNumber: 80,
        columnNumber: 3
    }, ("TURBOPACK compile-time value", void 0)));
DropdownMenuItem.displayName = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Item"].displayName;
const DropdownMenuCheckboxItem = /*#__PURE__*/ __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["forwardRef"](({ className, children, checked, ...props }, ref)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["CheckboxItem"], {
        ref: ref,
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("relative flex cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none transition-colors focus:bg-surface-hover focus:text-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50", className),
        checked: checked,
        ...props,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                className: "absolute left-2 flex h-3.5 w-3.5 items-center justify-center",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ItemIndicator"], {
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        className: "h-2 w-2 rounded-full bg-primary"
                    }, void 0, false, {
                        fileName: "[project]/components/ui/dropdown-menu.tsx",
                        lineNumber: 107,
                        columnNumber: 9
                    }, ("TURBOPACK compile-time value", void 0))
                }, void 0, false, {
                    fileName: "[project]/components/ui/dropdown-menu.tsx",
                    lineNumber: 106,
                    columnNumber: 7
                }, ("TURBOPACK compile-time value", void 0))
            }, void 0, false, {
                fileName: "[project]/components/ui/dropdown-menu.tsx",
                lineNumber: 105,
                columnNumber: 5
            }, ("TURBOPACK compile-time value", void 0)),
            children
        ]
    }, void 0, true, {
        fileName: "[project]/components/ui/dropdown-menu.tsx",
        lineNumber: 96,
        columnNumber: 3
    }, ("TURBOPACK compile-time value", void 0)));
DropdownMenuCheckboxItem.displayName = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["CheckboxItem"].displayName;
const DropdownMenuRadioItem = /*#__PURE__*/ __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["forwardRef"](({ className, children, ...props }, ref)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["RadioItem"], {
        ref: ref,
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("relative flex cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none transition-colors focus:bg-surface-hover focus:text-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50", className),
        ...props,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                className: "absolute left-2 flex h-3.5 w-3.5 items-center justify-center",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ItemIndicator"], {
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        className: "h-2 w-2 rounded-full bg-primary"
                    }, void 0, false, {
                        fileName: "[project]/components/ui/dropdown-menu.tsx",
                        lineNumber: 129,
                        columnNumber: 9
                    }, ("TURBOPACK compile-time value", void 0))
                }, void 0, false, {
                    fileName: "[project]/components/ui/dropdown-menu.tsx",
                    lineNumber: 128,
                    columnNumber: 7
                }, ("TURBOPACK compile-time value", void 0))
            }, void 0, false, {
                fileName: "[project]/components/ui/dropdown-menu.tsx",
                lineNumber: 127,
                columnNumber: 5
            }, ("TURBOPACK compile-time value", void 0)),
            children
        ]
    }, void 0, true, {
        fileName: "[project]/components/ui/dropdown-menu.tsx",
        lineNumber: 119,
        columnNumber: 3
    }, ("TURBOPACK compile-time value", void 0)));
DropdownMenuRadioItem.displayName = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["RadioItem"].displayName;
const DropdownMenuLabel = /*#__PURE__*/ __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["forwardRef"](({ className, inset, ...props }, ref)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Label"], {
        ref: ref,
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("px-2 py-1.5 text-sm font-semibold", inset && "pl-8", className),
        ...props
    }, void 0, false, {
        fileName: "[project]/components/ui/dropdown-menu.tsx",
        lineNumber: 143,
        columnNumber: 3
    }, ("TURBOPACK compile-time value", void 0)));
DropdownMenuLabel.displayName = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Label"].displayName;
const DropdownMenuSeparator = /*#__PURE__*/ __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["forwardRef"](({ className, ...props }, ref)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Separator"], {
        ref: ref,
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("-mx-1 my-1 h-px bg-border", className),
        ...props
    }, void 0, false, {
        fileName: "[project]/components/ui/dropdown-menu.tsx",
        lineNumber: 155,
        columnNumber: 3
    }, ("TURBOPACK compile-time value", void 0)));
DropdownMenuSeparator.displayName = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Separator"].displayName;
const DropdownMenuShortcut = ({ className, ...props })=>{
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("ml-auto text-xs tracking-widest opacity-60", className),
        ...props
    }, void 0, false, {
        fileName: "[project]/components/ui/dropdown-menu.tsx",
        lineNumber: 164,
        columnNumber: 10
    }, ("TURBOPACK compile-time value", void 0));
};
DropdownMenuShortcut.displayName = "DropdownMenuShortcut";
;
}),
"[project]/components/layout/top-nav.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "TopNav",
    ()=>TopNav
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$user$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__User$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/user.js [app-ssr] (ecmascript) <export default as User>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$bell$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Bell$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/bell.js [app-ssr] (ecmascript) <export default as Bell>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/settings.js [app-ssr] (ecmascript) <export default as Settings>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$moon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Moon$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/moon.js [app-ssr] (ecmascript) <export default as Moon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sun$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Sun$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/sun.js [app-ssr] (ecmascript) <export default as Sun>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$out$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__LogOut$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/log-out.js [app-ssr] (ecmascript) <export default as LogOut>");
var __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$theme$2d$context$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/contexts/theme-context.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/hooks.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$authSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/authSlice.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/ui/dropdown-menu.tsx [app-ssr] (ecmascript)");
"use client";
;
;
;
;
;
;
;
;
function TopNav() {
    const { theme, toggleTheme } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$theme$2d$context$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useTheme"])();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useRouter"])();
    const dispatch = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAppDispatch"])();
    const { user } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAppSelector"])((state)=>state.auth);
    const { unreadCount } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAppSelector"])((state)=>state.alerts);
    const [mounted, setMounted] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        setMounted(true);
    }, []);
    const handleLogout = async ()=>{
        try {
            await dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$authSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["logout"])());
            router.push("/auth/login");
        } catch (error) {
            console.error("Logout error:", error);
            // Still redirect even if logout fails
            router.push("/auth/login");
        }
    };
    // Safety check for user data
    const userName = user?.full_name || "User";
    const userEmail = user?.email || "";
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "h-16 border-b border-border bg-sidebar flex items-center justify-between px-6",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                        className: "text-xl font-semibold text-foreground",
                        children: "Change Data Capture Platform"
                    }, void 0, false, {
                        fileName: "[project]/components/layout/top-nav.tsx",
                        lineNumber: 48,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "text-sm text-foreground-muted",
                        children: "Real-time Replication & Monitoring"
                    }, void 0, false, {
                        fileName: "[project]/components/layout/top-nav.tsx",
                        lineNumber: 49,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/layout/top-nav.tsx",
                lineNumber: 47,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex items-center gap-4",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        onClick: ()=>router.push("/errors"),
                        className: "relative p-2 hover:bg-surface-hover rounded-lg transition-colors hover:text-primary",
                        "aria-label": "Notifications",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$bell$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Bell$3e$__["Bell"], {
                                className: "w-5 h-5 text-foreground-muted hover:text-primary transition-colors"
                            }, void 0, false, {
                                fileName: "[project]/components/layout/top-nav.tsx",
                                lineNumber: 58,
                                columnNumber: 11
                            }, this),
                            mounted && unreadCount > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                className: "absolute top-0 right-0 w-4 h-4 bg-error text-white text-xs rounded-full flex items-center justify-center",
                                children: unreadCount > 9 ? '9+' : unreadCount
                            }, void 0, false, {
                                fileName: "[project]/components/layout/top-nav.tsx",
                                lineNumber: 60,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/layout/top-nav.tsx",
                        lineNumber: 53,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        className: "p-2 hover:bg-surface-hover rounded-lg transition-colors hover:text-primary",
                        "aria-label": "Settings",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__["Settings"], {
                            className: "w-5 h-5 text-foreground-muted hover:text-primary transition-colors"
                        }, void 0, false, {
                            fileName: "[project]/components/layout/top-nav.tsx",
                            lineNumber: 66,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/layout/top-nav.tsx",
                        lineNumber: 65,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        onClick: toggleTheme,
                        className: "p-2 hover:bg-surface-hover rounded-lg transition-colors hover:text-primary",
                        "aria-label": "Toggle theme",
                        suppressHydrationWarning: true,
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sun$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Sun$3e$__["Sun"], {
                                className: `w-5 h-5 text-foreground-muted ${mounted && theme === "dark" ? "block" : "hidden"}`
                            }, void 0, false, {
                                fileName: "[project]/components/layout/top-nav.tsx",
                                lineNumber: 74,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$moon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Moon$3e$__["Moon"], {
                                className: `w-5 h-5 text-foreground-muted ${mounted && theme === "light" ? "block" : "hidden"}`
                            }, void 0, false, {
                                fileName: "[project]/components/layout/top-nav.tsx",
                                lineNumber: 75,
                                columnNumber: 11
                            }, this),
                            !mounted && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$moon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Moon$3e$__["Moon"], {
                                className: "w-5 h-5 text-foreground-muted"
                            }, void 0, false, {
                                fileName: "[project]/components/layout/top-nav.tsx",
                                lineNumber: 76,
                                columnNumber: 24
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/layout/top-nav.tsx",
                        lineNumber: 68,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        suppressHydrationWarning: true,
                        children: mounted ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["DropdownMenu"], {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["DropdownMenuTrigger"], {
                                    asChild: true,
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        className: "p-2 hover:bg-surface-hover rounded-lg transition-colors hover:text-primary",
                                        "aria-label": "User menu",
                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$user$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__User$3e$__["User"], {
                                            className: "w-5 h-5 text-foreground-muted hover:text-primary transition-colors"
                                        }, void 0, false, {
                                            fileName: "[project]/components/layout/top-nav.tsx",
                                            lineNumber: 85,
                                            columnNumber: 19
                                        }, this)
                                    }, void 0, false, {
                                        fileName: "[project]/components/layout/top-nav.tsx",
                                        lineNumber: 84,
                                        columnNumber: 17
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/components/layout/top-nav.tsx",
                                    lineNumber: 83,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["DropdownMenuContent"], {
                                    align: "end",
                                    className: "bg-surface border-border",
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["DropdownMenuLabel"], {
                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                className: "flex flex-col space-y-1",
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                        className: "text-sm font-medium text-foreground",
                                                        children: userName
                                                    }, void 0, false, {
                                                        fileName: "[project]/components/layout/top-nav.tsx",
                                                        lineNumber: 91,
                                                        columnNumber: 21
                                                    }, this),
                                                    userEmail && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                        className: "text-xs text-foreground-muted",
                                                        children: userEmail
                                                    }, void 0, false, {
                                                        fileName: "[project]/components/layout/top-nav.tsx",
                                                        lineNumber: 92,
                                                        columnNumber: 35
                                                    }, this)
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/components/layout/top-nav.tsx",
                                                lineNumber: 90,
                                                columnNumber: 19
                                            }, this)
                                        }, void 0, false, {
                                            fileName: "[project]/components/layout/top-nav.tsx",
                                            lineNumber: 89,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["DropdownMenuSeparator"], {}, void 0, false, {
                                            fileName: "[project]/components/layout/top-nav.tsx",
                                            lineNumber: 95,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["DropdownMenuItem"], {
                                            onClick: ()=>router.push("/settings"),
                                            className: "cursor-pointer",
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__["Settings"], {
                                                    className: "w-4 h-4 mr-2"
                                                }, void 0, false, {
                                                    fileName: "[project]/components/layout/top-nav.tsx",
                                                    lineNumber: 97,
                                                    columnNumber: 19
                                                }, this),
                                                "Settings"
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/layout/top-nav.tsx",
                                            lineNumber: 96,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["DropdownMenuSeparator"], {}, void 0, false, {
                                            fileName: "[project]/components/layout/top-nav.tsx",
                                            lineNumber: 100,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["DropdownMenuItem"], {
                                            onClick: handleLogout,
                                            className: "cursor-pointer text-error focus:text-error",
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$out$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__LogOut$3e$__["LogOut"], {
                                                    className: "w-4 h-4 mr-2"
                                                }, void 0, false, {
                                                    fileName: "[project]/components/layout/top-nav.tsx",
                                                    lineNumber: 102,
                                                    columnNumber: 19
                                                }, this),
                                                "Logout"
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/layout/top-nav.tsx",
                                            lineNumber: 101,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/layout/top-nav.tsx",
                                    lineNumber: 88,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/layout/top-nav.tsx",
                            lineNumber: 82,
                            columnNumber: 13
                        }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            className: "p-2 hover:bg-surface-hover rounded-lg transition-colors hover:text-primary",
                            "aria-label": "User menu",
                            disabled: true,
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$user$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__User$3e$__["User"], {
                                className: "w-5 h-5 text-foreground-muted hover:text-primary transition-colors"
                            }, void 0, false, {
                                fileName: "[project]/components/layout/top-nav.tsx",
                                lineNumber: 109,
                                columnNumber: 15
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/components/layout/top-nav.tsx",
                            lineNumber: 108,
                            columnNumber: 13
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/layout/top-nav.tsx",
                        lineNumber: 80,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/layout/top-nav.tsx",
                lineNumber: 52,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/layout/top-nav.tsx",
        lineNumber: 46,
        columnNumber: 5
    }, this);
}
}),
"[project]/lib/store/slices/alertsSlice.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Alerts and Errors Redux slice for real-time error tracking
 */ __turbopack_context__.s([
    "addAlert",
    ()=>addAlert,
    "addAlerts",
    ()=>addAlerts,
    "clearAlerts",
    ()=>clearAlerts,
    "default",
    ()=>__TURBOPACK__default__export__,
    "markAllAsRead",
    ()=>markAllAsRead,
    "removeAlert",
    ()=>removeAlert,
    "updateAlertStatus",
    ()=>updateAlertStatus
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/@reduxjs/toolkit/dist/redux-toolkit.modern.mjs [app-ssr] (ecmascript) <locals>");
;
const initialState = {
    alerts: [],
    unreadCount: 0,
    lastNotificationTime: null
};
const alertsSlice = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createSlice"])({
    name: 'alerts',
    initialState,
    reducers: {
        addAlert: (state, action)=>{
            // Check if alert already exists (prevent duplicates)
            const exists = state.alerts.some((a)=>a.id === action.payload.id);
            if (!exists) {
                state.alerts.unshift(action.payload); // Add to beginning
                if (action.payload.status === 'unresolved') {
                    state.unreadCount++;
                }
                // Keep only last 1000 alerts
                if (state.alerts.length > 1000) {
                    state.alerts = state.alerts.slice(0, 1000);
                }
            }
        },
        addAlerts: (state, action)=>{
            action.payload.forEach((alert)=>{
                const exists = state.alerts.some((a)=>a.id === alert.id);
                if (!exists) {
                    state.alerts.unshift(alert);
                    if (alert.status === 'unresolved') {
                        state.unreadCount++;
                    }
                }
            });
            // Keep only last 1000 alerts
            if (state.alerts.length > 1000) {
                state.alerts = state.alerts.slice(0, 1000);
            }
        },
        updateAlertStatus: (state, action)=>{
            const alert = state.alerts.find((a)=>a.id === action.payload.id);
            if (alert) {
                const wasUnresolved = alert.status === 'unresolved';
                alert.status = action.payload.status;
                if (wasUnresolved && action.payload.status !== 'unresolved') {
                    state.unreadCount = Math.max(0, state.unreadCount - 1);
                } else if (!wasUnresolved && action.payload.status === 'unresolved') {
                    state.unreadCount++;
                }
            }
        },
        markAllAsRead: (state)=>{
            state.unreadCount = 0;
            state.lastNotificationTime = new Date().toISOString();
        },
        clearAlerts: (state)=>{
            state.alerts = [];
            state.unreadCount = 0;
        },
        removeAlert: (state, action)=>{
            const alert = state.alerts.find((a)=>a.id === action.payload);
            if (alert && alert.status === 'unresolved') {
                state.unreadCount = Math.max(0, state.unreadCount - 1);
            }
            state.alerts = state.alerts.filter((a)=>a.id !== action.payload);
        }
    }
});
const { addAlert, addAlerts, updateAlertStatus, markAllAsRead, clearAlerts, removeAlert } = alertsSlice.actions;
const __TURBOPACK__default__export__ = alertsSlice.reducer;
}),
"[project]/components/alerts/alert-sync.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Component to sync errors from connections, pipelines, and events to alerts
 */ __turbopack_context__.s([
    "AlertSync",
    ()=>AlertSync
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/hooks.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/alertsSlice.ts [app-ssr] (ecmascript)");
"use client";
;
;
;
function AlertSync() {
    const dispatch = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAppDispatch"])();
    const { connections, error: connectionError } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAppSelector"])((state)=>state.connections);
    const { pipelines, error: pipelineError } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAppSelector"])((state)=>state.pipelines);
    const { events } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAppSelector"])((state)=>state.monitoring);
    // Sync connection errors
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        if (connectionError) {
            dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["addAlert"])({
                id: `conn_error_${Date.now()}`,
                type: 'error',
                source: 'connection',
                message: connectionError,
                timestamp: new Date().toISOString(),
                status: 'unresolved',
                severity: 'high'
            }));
        }
    }, [
        connectionError,
        dispatch
    ]);
    // Sync pipeline errors
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        if (pipelineError) {
            dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["addAlert"])({
                id: `pipeline_error_${Date.now()}`,
                type: 'error',
                source: 'pipeline',
                message: pipelineError,
                timestamp: new Date().toISOString(),
                status: 'unresolved',
                severity: 'high'
            }));
        }
    }, [
        pipelineError,
        dispatch
    ]);
    // Sync connection test failures
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        const connectionsArray = Array.isArray(connections) ? connections : [];
        connectionsArray.forEach((conn)=>{
            if (conn.last_test_status === 'failed' || !conn.is_active && conn.last_tested_at) {
                dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["addAlert"])({
                    id: `conn_test_${conn.id}_${conn.last_tested_at}`,
                    type: 'error',
                    source: 'connection',
                    sourceId: conn.id,
                    sourceName: conn.name,
                    message: `Connection test failed: ${conn.name}`,
                    details: conn.last_test_status || 'Connection inactive',
                    timestamp: conn.last_tested_at || conn.updated_at || conn.created_at,
                    status: 'unresolved',
                    severity: 'high'
                }));
            }
        });
    }, [
        connections,
        dispatch
    ]);
    // Sync pipeline errors
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        const pipelinesArray = Array.isArray(pipelines) ? pipelines : [];
        pipelinesArray.forEach((pipeline)=>{
            if (pipeline.status === 'error') {
                dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["addAlert"])({
                    id: `pipeline_status_${pipeline.id}_${pipeline.updated_at || pipeline.created_at}`,
                    type: 'error',
                    source: 'pipeline',
                    sourceId: pipeline.id,
                    sourceName: pipeline.name,
                    message: `Pipeline error: ${pipeline.name}`,
                    details: `Pipeline status: ${pipeline.status}`,
                    timestamp: pipeline.updated_at || pipeline.created_at,
                    status: 'unresolved',
                    severity: 'critical'
                }));
            }
        });
    }, [
        pipelines,
        dispatch
    ]);
    // Sync replication event errors
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        const eventsArray = Array.isArray(events) ? events : [];
        const failedEvents = eventsArray.filter((e)=>e.status === 'failed' || e.status === 'error').slice(0, 100) // Limit to recent 100 failed events
        ;
        if (failedEvents.length > 0) {
            const alerts = failedEvents.map((event)=>({
                    id: `replication_${event.id}`,
                    type: 'error',
                    source: 'replication',
                    sourceId: event.pipeline_id,
                    message: `Replication failed: ${event.event_type} on ${event.table_name}`,
                    details: `Status: ${event.status}`,
                    timestamp: event.created_at || new Date().toISOString(),
                    status: 'unresolved',
                    severity: event.latency_ms && event.latency_ms > 10000 ? 'critical' : 'high',
                    table: event.table_name
                }));
            dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["addAlerts"])(alerts));
        }
    }, [
        events,
        dispatch
    ]);
    return null // This is a sync component, no UI
    ;
}
}),
"[project]/components/ui/button.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "Button",
    ()=>Button,
    "buttonVariants",
    ()=>buttonVariants
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$slot$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@radix-ui/react-slot/dist/index.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$class$2d$variance$2d$authority$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/class-variance-authority/dist/index.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/utils.ts [app-ssr] (ecmascript)");
;
;
;
;
const buttonVariants = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$class$2d$variance$2d$authority$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cva"])("inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive", {
    variants: {
        variant: {
            default: 'bg-primary text-primary-foreground hover:bg-primary/90',
            destructive: 'bg-destructive text-white hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60',
            outline: 'border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground active:bg-accent/90 active:text-accent-foreground dark:bg-input/30 dark:border-input dark:hover:bg-input/50',
            secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/90 active:bg-secondary/80',
            ghost: 'hover:bg-accent hover:text-accent-foreground active:bg-accent/90 active:text-accent-foreground dark:hover:bg-accent/50',
            link: 'text-primary underline-offset-4 hover:underline'
        },
        size: {
            default: 'h-9 px-4 py-2 has-[>svg]:px-3',
            sm: 'h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5',
            lg: 'h-10 rounded-md px-6 has-[>svg]:px-4',
            icon: 'size-9',
            'icon-sm': 'size-8',
            'icon-lg': 'size-10'
        }
    },
    defaultVariants: {
        variant: 'default',
        size: 'default'
    }
});
function Button({ className, variant, size, asChild = false, ...props }) {
    const Comp = asChild ? __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$slot$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Slot"] : 'button';
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(Comp, {
        "data-slot": "button",
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])(buttonVariants({
            variant,
            size,
            className
        })),
        ...props
    }, void 0, false, {
        fileName: "[project]/components/ui/button.tsx",
        lineNumber: 52,
        columnNumber: 5
    }, this);
}
;
}),
"[project]/components/alerts/top-alert-bar.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Top alert bar component to show critical alerts at the top of the page
 */ __turbopack_context__.s([
    "TopAlertBar",
    ()=>TopAlertBar
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/hooks.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/alertsSlice.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/x.js [app-ssr] (ecmascript) <export default as X>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__AlertTriangle$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/triangle-alert.js [app-ssr] (ecmascript) <export default as AlertTriangle>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$circle$2d$alert$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__AlertCircle$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/circle-alert.js [app-ssr] (ecmascript) <export default as AlertCircle>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$info$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Info$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/info.js [app-ssr] (ecmascript) <export default as Info>");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/ui/button.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$date$2d$fns$2f$formatDistanceToNow$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/date-fns/formatDistanceToNow.js [app-ssr] (ecmascript)");
"use client";
;
;
;
;
;
;
;
function TopAlertBar() {
    const dispatch = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAppDispatch"])();
    const { alerts, unreadCount } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAppSelector"])((state)=>state.alerts);
    const [dismissedAlerts, setDismissedAlerts] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(new Set());
    // Get critical/unresolved alerts - memoized to prevent unnecessary recalculations
    const criticalAlerts = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useMemo"])(()=>{
        return alerts.filter((a)=>a.status === 'unresolved' && (a.severity === 'critical' || a.severity === 'high') && !dismissedAlerts.has(a.id)).slice(0, 3) // Show max 3 alerts
        ;
    }, [
        alerts,
        dismissedAlerts
    ]);
    // Request notification permission
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        if (("TURBOPACK compile-time value", "undefined") !== 'undefined' && 'Notification' in window && Notification.permission === 'default') //TURBOPACK unreachable
        ;
    }, []);
    // Show browser notifications for new critical alerts
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        if (criticalAlerts.length > 0 && ("TURBOPACK compile-time value", "undefined") !== 'undefined' && 'Notification' in window) //TURBOPACK unreachable
        ;
    }, [
        criticalAlerts,
        dismissedAlerts
    ]);
    // Memoize handlers to prevent infinite loops
    const handleAcknowledge = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])((alertId)=>{
        dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["updateAlertStatus"])({
            id: alertId,
            status: 'acknowledged'
        }));
        setDismissedAlerts((prev)=>{
            const newSet = new Set(prev);
            newSet.add(alertId);
            return newSet;
        });
    }, [
        dispatch
    ]);
    const handleDismiss = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])((alertId)=>{
        setDismissedAlerts((prev)=>{
            const newSet = new Set(prev);
            newSet.add(alertId);
            return newSet;
        });
    }, []);
    if (criticalAlerts.length === 0) {
        return null;
    }
    const getAlertIcon = (type, severity)=>{
        if (severity === 'critical') {
            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$circle$2d$alert$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__AlertCircle$3e$__["AlertCircle"], {
                className: "w-5 h-5 text-destructive"
            }, void 0, false, {
                fileName: "[project]/components/alerts/top-alert-bar.tsx",
                lineNumber: 74,
                columnNumber: 14
            }, this);
        }
        if (type === 'error' || severity === 'high') {
            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__AlertTriangle$3e$__["AlertTriangle"], {
                className: "w-5 h-5 text-error"
            }, void 0, false, {
                fileName: "[project]/components/alerts/top-alert-bar.tsx",
                lineNumber: 77,
                columnNumber: 14
            }, this);
        }
        if (type === 'warning') {
            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__AlertTriangle$3e$__["AlertTriangle"], {
                className: "w-5 h-5 text-warning"
            }, void 0, false, {
                fileName: "[project]/components/alerts/top-alert-bar.tsx",
                lineNumber: 80,
                columnNumber: 14
            }, this);
        }
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$info$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Info$3e$__["Info"], {
            className: "w-5 h-5 text-info"
        }, void 0, false, {
            fileName: "[project]/components/alerts/top-alert-bar.tsx",
            lineNumber: 82,
            columnNumber: 12
        }, this);
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "border-b border-border bg-surface",
        children: [
            criticalAlerts.map((alert)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: `px-6 py-3 flex items-center gap-4 ${alert.severity === 'critical' ? 'bg-destructive/10 border-l-4 border-destructive' : alert.severity === 'high' ? 'bg-error/10 border-l-4 border-error' : 'bg-warning/10 border-l-4 border-warning'}`,
                    children: [
                        getAlertIcon(alert.type, alert.severity),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "flex-1",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                    className: "text-sm font-semibold text-foreground",
                                    children: [
                                        alert.sourceName ? `${alert.sourceName}: ` : '',
                                        alert.message
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/alerts/top-alert-bar.tsx",
                                    lineNumber: 98,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                    className: "text-xs text-foreground-muted mt-0.5",
                                    children: (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$date$2d$fns$2f$formatDistanceToNow$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["formatDistanceToNow"])(new Date(alert.timestamp), {
                                        addSuffix: true
                                    })
                                }, void 0, false, {
                                    fileName: "[project]/components/alerts/top-alert-bar.tsx",
                                    lineNumber: 101,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/alerts/top-alert-bar.tsx",
                            lineNumber: 97,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "flex items-center gap-2",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Button"], {
                                    size: "sm",
                                    variant: "ghost",
                                    onClick: (e)=>{
                                        e.preventDefault();
                                        e.stopPropagation();
                                        handleAcknowledge(alert.id);
                                    },
                                    className: "text-xs h-7",
                                    children: "Acknowledge"
                                }, void 0, false, {
                                    fileName: "[project]/components/alerts/top-alert-bar.tsx",
                                    lineNumber: 106,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Button"], {
                                    size: "sm",
                                    variant: "ghost",
                                    onClick: (e)=>{
                                        e.preventDefault();
                                        e.stopPropagation();
                                        handleDismiss(alert.id);
                                    },
                                    className: "text-xs h-7 px-2",
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                                        className: "w-4 h-4"
                                    }, void 0, false, {
                                        fileName: "[project]/components/alerts/top-alert-bar.tsx",
                                        lineNumber: 128,
                                        columnNumber: 15
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/components/alerts/top-alert-bar.tsx",
                                    lineNumber: 118,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/alerts/top-alert-bar.tsx",
                            lineNumber: 105,
                            columnNumber: 11
                        }, this)
                    ]
                }, alert.id, true, {
                    fileName: "[project]/components/alerts/top-alert-bar.tsx",
                    lineNumber: 88,
                    columnNumber: 9
                }, this)),
            unreadCount > criticalAlerts.length && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "px-6 py-2 bg-surface-hover text-center",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Button"], {
                    variant: "ghost",
                    size: "sm",
                    onClick: ()=>dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["markAllAsRead"])()),
                    className: "text-xs text-foreground-muted hover:text-foreground",
                    children: [
                        unreadCount - criticalAlerts.length,
                        " more alert",
                        unreadCount - criticalAlerts.length !== 1 ? 's' : '',
                        " - View all"
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/alerts/top-alert-bar.tsx",
                    lineNumber: 135,
                    columnNumber: 11
                }, this)
            }, void 0, false, {
                fileName: "[project]/components/alerts/top-alert-bar.tsx",
                lineNumber: 134,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/alerts/top-alert-bar.tsx",
        lineNumber: 86,
        columnNumber: 5
    }, this);
}
}),
"[project]/components/layout/root-layout-wrapper.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "RootLayoutWrapper",
    ()=>RootLayoutWrapper
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$layout$2f$sidebar$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/layout/sidebar.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$layout$2f$top$2d$nav$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/layout/top-nav.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$theme$2d$context$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/contexts/theme-context.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$sidebar$2d$context$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/contexts/sidebar-context.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$alerts$2f$alert$2d$sync$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/alerts/alert-sync.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$alerts$2f$top$2d$alert$2d$bar$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/alerts/top-alert-bar.tsx [app-ssr] (ecmascript)");
"use client";
;
;
;
;
;
;
;
;
function RootLayoutWrapper({ children }) {
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["usePathname"])();
    const isAuthPage = pathname?.startsWith("/auth");
    // Auth pages (login, signup) should not have dashboard layout
    if (isAuthPage) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$theme$2d$context$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ThemeProvider"], {
            children: children
        }, void 0, false, {
            fileName: "[project]/components/layout/root-layout-wrapper.tsx",
            lineNumber: 19,
            columnNumber: 7
        }, this);
    }
    // Dashboard and other pages get the full layout with sidebar and top nav
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$theme$2d$context$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ThemeProvider"], {
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$sidebar$2d$context$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["SidebarProvider"], {
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex h-screen bg-sidebar",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$layout$2f$sidebar$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Sidebar"], {}, void 0, false, {
                        fileName: "[project]/components/layout/root-layout-wrapper.tsx",
                        lineNumber: 30,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex-1 flex flex-col overflow-hidden bg-sidebar",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$alerts$2f$alert$2d$sync$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["AlertSync"], {}, void 0, false, {
                                fileName: "[project]/components/layout/root-layout-wrapper.tsx",
                                lineNumber: 34,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$layout$2f$top$2d$nav$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["TopNav"], {}, void 0, false, {
                                fileName: "[project]/components/layout/root-layout-wrapper.tsx",
                                lineNumber: 35,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$alerts$2f$top$2d$alert$2d$bar$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["TopAlertBar"], {}, void 0, false, {
                                fileName: "[project]/components/layout/root-layout-wrapper.tsx",
                                lineNumber: 36,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
                                className: "flex-1 overflow-y-auto bg-sidebar",
                                children: children
                            }, void 0, false, {
                                fileName: "[project]/components/layout/root-layout-wrapper.tsx",
                                lineNumber: 39,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/layout/root-layout-wrapper.tsx",
                        lineNumber: 33,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/layout/root-layout-wrapper.tsx",
                lineNumber: 29,
                columnNumber: 9
            }, this)
        }, void 0, false, {
            fileName: "[project]/components/layout/root-layout-wrapper.tsx",
            lineNumber: 28,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/layout/root-layout-wrapper.tsx",
        lineNumber: 27,
        columnNumber: 5
    }, this);
}
}),
"[project]/lib/store/slices/connectionSlice.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Connection Redux slice
 */ __turbopack_context__.s([
    "clearError",
    ()=>clearError,
    "createConnection",
    ()=>createConnection,
    "default",
    ()=>__TURBOPACK__default__export__,
    "deleteConnection",
    ()=>deleteConnection,
    "fetchConnection",
    ()=>fetchConnection,
    "fetchConnections",
    ()=>fetchConnections,
    "setSelectedConnection",
    ()=>setSelectedConnection,
    "testConnection",
    ()=>testConnection,
    "updateConnection",
    ()=>updateConnection
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/@reduxjs/toolkit/dist/redux-toolkit.modern.mjs [app-ssr] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api/client.ts [app-ssr] (ecmascript)");
;
;
// Utility to ensure error is always a string
const ensureStringError = (error)=>{
    if (!error) return 'An error occurred';
    if (typeof error === 'string') return error;
    if (Array.isArray(error)) {
        return error.map((err)=>{
            if (typeof err === 'string') return err;
            const field = err.loc?.join('.') || 'field';
            return `${field}: ${err.msg || err.message || 'Invalid value'}`;
        }).join(', ');
    }
    if (typeof error === 'object') {
        return error.message || error.msg || error.detail || JSON.stringify(error);
    }
    return String(error);
};
const initialState = {
    connections: [],
    selectedConnection: null,
    isLoading: false,
    error: null
};
const fetchConnections = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('connections/fetchAll', async (_, { rejectWithValue })=>{
    try {
        return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].getConnections();
    } catch (error) {
        // Provide more helpful error messages for timeouts
        if (error.isTimeout) {
            return rejectWithValue('Request timeout: The server took too long to respond. This may indicate a database connection issue. Please check if PostgreSQL is running and the backend is accessible.');
        }
        if (error.isNetworkError) {
            return rejectWithValue('Network error: Cannot connect to the backend server. Please ensure it is running on http://localhost:8000');
        }
        return rejectWithValue(error.message || 'Failed to fetch connections');
    }
});
const fetchConnection = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('connections/fetchOne', async (id)=>{
    return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].getConnection(id);
});
// Helper function to extract error message from FastAPI error response
const extractErrorMessage = (error)=>{
    if (!error?.response?.data) {
        return error?.message || 'An unexpected error occurred';
    }
    const detail = error.response.data.detail;
    // If detail is a string, return it
    if (typeof detail === 'string') {
        return detail;
    }
    // If detail is an array (validation errors), format them
    if (Array.isArray(detail)) {
        return detail.map((err)=>{
            const field = err.loc?.join('.') || 'field';
            return `${field}: ${err.msg || 'Invalid value'}`;
        }).join(', ');
    }
    // If detail is an object, try to get message
    if (typeof detail === 'object' && detail !== null) {
        return detail.message || detail.msg || JSON.stringify(detail);
    }
    return 'Failed to create connection';
};
const createConnection = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('connections/create', async (connectionData, { rejectWithValue })=>{
    try {
        return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].createConnection(connectionData);
    } catch (error) {
        return rejectWithValue(extractErrorMessage(error));
    }
});
const updateConnection = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('connections/update', async ({ id, data }, { rejectWithValue })=>{
    try {
        return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].updateConnection(id, data);
    } catch (error) {
        return rejectWithValue(extractErrorMessage(error));
    }
});
const deleteConnection = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('connections/delete', async (id, { rejectWithValue })=>{
    try {
        await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].deleteConnection(id);
        return id;
    } catch (error) {
        return rejectWithValue(extractErrorMessage(error));
    }
});
const testConnection = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('connections/test', async (id, { rejectWithValue })=>{
    try {
        return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].testConnection(id);
    } catch (error) {
        // Handle timeout errors specifically
        if (error.isTimeout || error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
            return rejectWithValue('Connection test timed out. The database server may be unreachable or the connection is taking too long. Please check network connectivity and firewall settings.');
        }
        // Handle network errors
        if (error.isNetworkError || error.code === 'ERR_NETWORK' || error.code === 'ECONNREFUSED') {
            return rejectWithValue('Network error: Cannot connect to the backend server. Please ensure it is running on http://localhost:8000');
        }
        // Extract error message from backend response
        return rejectWithValue(extractErrorMessage(error));
    }
});
const connectionSlice = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createSlice"])({
    name: 'connections',
    initialState,
    reducers: {
        setSelectedConnection: (state, action)=>{
            state.selectedConnection = action.payload;
        },
        clearError: (state)=>{
            state.error = null;
        }
    },
    extraReducers: (builder)=>{
        builder.addCase(fetchConnections.pending, (state)=>{
            state.isLoading = true;
            state.error = null;
        }).addCase(fetchConnections.fulfilled, (state, action)=>{
            state.isLoading = false;
            state.connections = action.payload;
        }).addCase(fetchConnections.rejected, (state, action)=>{
            state.isLoading = false;
            state.error = ensureStringError(action.payload || action.error.message || 'Failed to fetch connections');
        }).addCase(createConnection.rejected, (state, action)=>{
            state.isLoading = false;
            state.error = ensureStringError(action.payload || 'Failed to create connection');
        }).addCase(updateConnection.rejected, (state, action)=>{
            state.isLoading = false;
            state.error = ensureStringError(action.payload || 'Failed to update connection');
        }).addCase(deleteConnection.rejected, (state, action)=>{
            state.isLoading = false;
            state.error = ensureStringError(action.payload || 'Failed to delete connection');
        }).addCase(testConnection.pending, (state)=>{
            state.isLoading = true;
            state.error = null;
        }).addCase(testConnection.fulfilled, (state, action)=>{
            state.isLoading = false;
            // Update the connection's test status in the list
            const connectionId = action.meta.arg;
            // Convert to string for comparison (backend uses string UUIDs, frontend might use numbers)
            const connectionIdStr = String(connectionId);
            const index = state.connections.findIndex((c)=>String(c.id) === connectionIdStr);
            if (index !== -1) {
                const result = action.payload;
                // Determine status: check result.success first, then result.status
                let testStatus = 'failed';
                if (result.success === true || result.success === 'true') {
                    testStatus = 'success';
                } else if (result.status === 'SUCCESS' || result.status === 'success') {
                    testStatus = 'success';
                } else if (result.success === false || result.status === 'FAILED' || result.status === 'failed') {
                    testStatus = 'failed';
                }
                console.log('[testConnection.fulfilled] Updating connection status:', {
                    connectionId,
                    connectionIdStr,
                    index,
                    result,
                    testStatus,
                    currentStatus: state.connections[index].last_test_status
                });
                state.connections[index] = {
                    ...state.connections[index],
                    last_test_status: testStatus,
                    last_tested_at: result.tested_at || new Date().toISOString()
                };
            } else {
                console.warn('[testConnection.fulfilled] Connection not found in state:', {
                    connectionId,
                    connectionIdStr,
                    availableIds: state.connections.map((c)=>({
                            id: c.id,
                            idType: typeof c.id
                        }))
                });
            }
        }).addCase(testConnection.rejected, (state, action)=>{
            state.isLoading = false;
            state.error = ensureStringError(action.payload || 'Connection test failed');
            // Update the connection's test status even on failure
            const connectionId = action.meta.arg;
            // Convert to string for comparison (backend uses string UUIDs, frontend might use numbers)
            const connectionIdStr = String(connectionId);
            const index = state.connections.findIndex((c)=>String(c.id) === connectionIdStr);
            if (index !== -1) {
                state.connections[index] = {
                    ...state.connections[index],
                    last_test_status: 'failed',
                    last_tested_at: new Date().toISOString()
                };
            }
        }).addCase(fetchConnection.fulfilled, (state, action)=>{
            state.selectedConnection = action.payload;
        }).addCase(createConnection.fulfilled, (state, action)=>{
            state.connections.push(action.payload);
        }).addCase(updateConnection.fulfilled, (state, action)=>{
            const index = state.connections.findIndex((c)=>c.id === action.payload.id);
            if (index !== -1) {
                state.connections[index] = action.payload;
            }
            if (state.selectedConnection?.id === action.payload.id) {
                state.selectedConnection = action.payload;
            }
        }).addCase(deleteConnection.fulfilled, (state, action)=>{
            state.connections = state.connections.filter((c)=>c.id !== action.payload);
            if (state.selectedConnection?.id === action.payload) {
                state.selectedConnection = null;
            }
        });
    }
});
const { setSelectedConnection, clearError } = connectionSlice.actions;
const __TURBOPACK__default__export__ = connectionSlice.reducer;
}),
"[project]/lib/store/slices/pipelineSlice.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Pipeline Redux slice
 */ __turbopack_context__.s([
    "clearError",
    ()=>clearError,
    "createPipeline",
    ()=>createPipeline,
    "default",
    ()=>__TURBOPACK__default__export__,
    "deletePipeline",
    ()=>deletePipeline,
    "fetchPipeline",
    ()=>fetchPipeline,
    "fetchPipelineStatus",
    ()=>fetchPipelineStatus,
    "fetchPipelines",
    ()=>fetchPipelines,
    "pausePipeline",
    ()=>pausePipeline,
    "setSelectedPipeline",
    ()=>setSelectedPipeline,
    "stopPipeline",
    ()=>stopPipeline,
    "triggerPipeline",
    ()=>triggerPipeline,
    "updatePipeline",
    ()=>updatePipeline
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/@reduxjs/toolkit/dist/redux-toolkit.modern.mjs [app-ssr] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api/client.ts [app-ssr] (ecmascript)");
;
;
const initialState = {
    pipelines: [],
    selectedPipeline: null,
    isLoading: false,
    error: null
};
const fetchPipelines = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/fetchAll', async (_, { rejectWithValue })=>{
    try {
        return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].getPipelines();
    } catch (error) {
        // Provide more helpful error messages for timeouts
        if (error.isTimeout) {
            return rejectWithValue('Request timeout: The server took too long to respond. This may indicate a database connection issue. Please check if PostgreSQL is running and the backend is accessible.');
        }
        if (error.isNetworkError) {
            return rejectWithValue('Network error: Cannot connect to the backend server. Please ensure it is running on http://localhost:8000');
        }
        return rejectWithValue(error.message || 'Failed to fetch pipelines');
    }
});
const fetchPipeline = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/fetchOne', async (id)=>{
    return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].getPipeline(id);
});
const createPipeline = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/create', async (pipelineData, { rejectWithValue })=>{
    try {
        return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].createPipeline(pipelineData);
    } catch (error) {
        // Extract error message from various possible locations
        let errorMessage = 'Failed to create pipeline';
        if (error.response?.data?.detail) {
            errorMessage = error.response.data.detail;
        } else if (error.response?.data?.message) {
            errorMessage = error.response.data.message;
        } else if (error.message) {
            errorMessage = error.message;
        } else if (typeof error === 'string') {
            errorMessage = error;
        }
        // Include full error info for debugging
        const errorInfo = {
            message: errorMessage,
            status: error.response?.status,
            data: error.response?.data,
            code: error.code,
            isTimeout: error.isTimeout,
            isNetworkError: error.isNetworkError
        };
        console.error('[Redux] createPipeline error:', errorInfo);
        return rejectWithValue(errorMessage);
    }
});
const updatePipeline = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/update', async ({ id, data }, { rejectWithValue })=>{
    try {
        return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].updatePipeline(String(id), data);
    } catch (error) {
        // Extract error message properly
        let errorMessage = 'Failed to update pipeline';
        if (error?.response?.data?.detail) {
            const detail = error.response.data.detail;
            if (Array.isArray(detail)) {
                // Pydantic validation errors
                errorMessage = detail.map((err)=>{
                    if (typeof err === 'object' && err.loc && err.msg) {
                        return `${err.loc.join('.')}: ${err.msg}`;
                    } else if (typeof err === 'object' && err.msg) {
                        return err.msg;
                    } else if (typeof err === 'string') {
                        return err;
                    } else {
                        return JSON.stringify(err);
                    }
                }).join(', ');
            } else if (typeof detail === 'string') {
                errorMessage = detail;
            } else {
                errorMessage = JSON.stringify(detail);
            }
        } else if (error?.response?.data?.message) {
            errorMessage = error.response.data.message;
        } else if (error?.message) {
            errorMessage = error.message;
        }
        return rejectWithValue(errorMessage);
    }
});
const deletePipeline = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/delete', async (id, { rejectWithValue })=>{
    try {
        await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].deletePipeline(id);
        return id;
    } catch (error) {
        return rejectWithValue(error.response?.data?.detail || 'Failed to delete pipeline');
    }
});
const triggerPipeline = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/trigger', async ({ id, runType }, { rejectWithValue, dispatch })=>{
    try {
        const result = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].triggerPipeline(String(id), runType);
        // Wait longer before refreshing to allow backend to fully update status
        await new Promise((resolve)=>setTimeout(resolve, 2000));
        // Refresh pipelines to get updated status
        dispatch(fetchPipelines());
        // Refresh again after a longer delay to ensure status is persisted
        setTimeout(()=>{
            dispatch(fetchPipelines());
        }, 4000);
        return result;
    } catch (error) {
        // Extract detailed error message
        let errorMessage = 'Failed to trigger pipeline';
        if (error?.response?.data?.detail) {
            errorMessage = error.response.data.detail;
        } else if (error?.response?.data?.message) {
            errorMessage = error.response.data.message;
        } else if (error?.message) {
            errorMessage = error.message;
        } else if (typeof error === 'string') {
            errorMessage = error;
        }
        // Remove redundant wrapping if present
        if (errorMessage.includes("Failed to trigger pipeline") && errorMessage.length > 25) {
            // Keep the actual error, remove the wrapper
            const parts = errorMessage.split("Failed to trigger pipeline");
            if (parts.length > 1) {
                errorMessage = parts[parts.length - 1].trim();
                if (errorMessage.startsWith(":")) {
                    errorMessage = errorMessage.substring(1).trim();
                }
            }
        }
        // Remove HTTP error wrapper if present
        if (errorMessage.includes("400 Client Error") || errorMessage.includes("Bad Request")) {
            // Extract the actual error message
            if (errorMessage.includes("for url:")) {
                const parts = errorMessage.split("for url:");
                if (parts.length > 0) {
                    errorMessage = parts[0].replace("400 Client Error:", "").replace("Bad Request", "").trim();
                }
            }
            // Also check if there's a detail in the response
            if (error?.response?.data?.detail) {
                errorMessage = error.response.data.detail;
            }
        }
        return rejectWithValue(errorMessage);
    }
});
const pausePipeline = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/pause', async (id, { rejectWithValue, dispatch })=>{
    try {
        const result = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].pausePipeline(String(id));
        // Refresh pipelines to get updated status
        dispatch(fetchPipelines());
        return result;
    } catch (error) {
        return rejectWithValue(error.response?.data?.detail || 'Failed to pause pipeline');
    }
});
const stopPipeline = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/stop', async (id, { rejectWithValue, dispatch })=>{
    try {
        const result = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].stopPipeline(String(id));
        // Refresh pipelines to get updated status
        dispatch(fetchPipelines());
        return result;
    } catch (error) {
        // Provide more detailed error message
        const errorMessage = error.response?.data?.detail || error.message || error.response?.data?.message || 'Failed to stop pipeline';
        console.error('[PipelineSlice] Stop pipeline error:', {
            error,
            response: error.response?.data,
            message: errorMessage
        });
        return rejectWithValue(errorMessage);
    }
});
const fetchPipelineStatus = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/fetchStatus', async (id)=>{
    return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].getPipelineStatus(id);
});
const pipelineSlice = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createSlice"])({
    name: 'pipelines',
    initialState,
    reducers: {
        setSelectedPipeline: (state, action)=>{
            state.selectedPipeline = action.payload;
        },
        clearError: (state)=>{
            state.error = null;
        }
    },
    extraReducers: (builder)=>{
        builder.addCase(fetchPipelines.pending, (state)=>{
            state.isLoading = true;
            state.error = null;
        }).addCase(fetchPipelines.fulfilled, (state, action)=>{
            state.isLoading = false;
            // Merge with existing pipelines to preserve optimistic updates
            // Only update if the backend status is more recent or different
            const newPipelines = action.payload;
            if (Array.isArray(newPipelines)) {
                // Create a map of new pipelines by ID
                const newPipelinesMap = new Map(newPipelines.map((p)=>[
                        String(p.id),
                        p
                    ]));
                // Update existing pipelines, but preserve optimistic 'active' status if backend hasn't caught up
                state.pipelines = state.pipelines.map((existingPipeline)=>{
                    const newPipeline = newPipelinesMap.get(String(existingPipeline.id));
                    if (newPipeline) {
                        // If we optimistically set it to active and backend still shows stopped/starting,
                        // keep it as active for a bit longer (backend might be slow to update)
                        if (existingPipeline.status === 'active' && newPipeline.status !== 'active' && newPipeline.status !== 'running') {
                            // Keep optimistic status for now, but update other fields
                            return {
                                ...newPipeline,
                                status: 'active'
                            };
                        }
                        return newPipeline;
                    }
                    return existingPipeline;
                });
                // Add any new pipelines that weren't in the existing list
                newPipelines.forEach((newPipeline)=>{
                    const exists = state.pipelines.some((p)=>String(p.id) === String(newPipeline.id));
                    if (!exists) {
                        state.pipelines.push(newPipeline);
                    }
                });
            } else {
                state.pipelines = newPipelines;
            }
        }).addCase(fetchPipelines.rejected, (state, action)=>{
            state.isLoading = false;
            state.error = action.error.message || 'Failed to fetch pipelines';
        }).addCase(fetchPipeline.fulfilled, (state, action)=>{
            state.selectedPipeline = action.payload;
        }).addCase(createPipeline.fulfilled, (state, action)=>{
            state.pipelines.push(action.payload);
        }).addCase(updatePipeline.fulfilled, (state, action)=>{
            const index = state.pipelines.findIndex((p)=>p.id === action.payload.id);
            if (index !== -1) {
                state.pipelines[index] = action.payload;
            }
            if (state.selectedPipeline?.id === action.payload.id) {
                state.selectedPipeline = action.payload;
            }
        }).addCase(deletePipeline.fulfilled, (state, action)=>{
            state.pipelines = state.pipelines.filter((p)=>p.id !== action.payload);
            if (state.selectedPipeline?.id === action.payload) {
                state.selectedPipeline = null;
            }
        }).addCase(triggerPipeline.pending, (state, action)=>{
            // Optimistically update status to active immediately
            const pipelineId = action.meta.arg.id;
            const pipeline = state.pipelines.find((p)=>String(p.id) === String(pipelineId));
            if (pipeline) {
                pipeline.status = 'active';
            }
            if (state.selectedPipeline && String(state.selectedPipeline.id) === String(pipelineId)) {
                state.selectedPipeline.status = 'active';
            }
        }).addCase(triggerPipeline.fulfilled, (state, action)=>{
            // Update pipeline status to active (in case pending didn't catch it)
            // The response might have 'id' field or 'pipeline_id'
            const pipelineId = action.payload?.id || action.payload?.pipeline_id || action.meta.arg.id;
            const pipeline = state.pipelines.find((p)=>String(p.id) === String(pipelineId));
            if (pipeline) {
                pipeline.status = 'active';
            }
            if (state.selectedPipeline && String(state.selectedPipeline.id) === String(pipelineId)) {
                state.selectedPipeline.status = 'active';
            }
        }).addCase(triggerPipeline.rejected, (state, action)=>{
            // Revert optimistic update on error
            const pipelineId = action.meta.arg.id;
            const pipeline = state.pipelines.find((p)=>String(p.id) === String(pipelineId));
            if (pipeline && pipeline.status === 'active') {
                // Only revert if we optimistically set it - check if it was actually started
                // Don't revert if backend says it's active but request failed
                pipeline.status = 'stopped';
            }
        }).addCase(pausePipeline.fulfilled, (state, action)=>{
            // Update pipeline status to paused
            const pipeline = state.pipelines.find((p)=>p.id === action.payload.id);
            if (pipeline) {
                pipeline.status = 'paused';
            }
            if (state.selectedPipeline && state.selectedPipeline.id === action.payload.id) {
                state.selectedPipeline.status = 'paused';
            }
        }).addCase(stopPipeline.fulfilled, (state, action)=>{
            // Update pipeline status to paused (stopped)
            const pipeline = state.pipelines.find((p)=>p.id === action.payload.id);
            if (pipeline) {
                pipeline.status = 'paused';
            }
            if (state.selectedPipeline && state.selectedPipeline.id === action.payload.id) {
                state.selectedPipeline.status = 'paused';
            }
        });
    }
});
const { setSelectedPipeline, clearError } = pipelineSlice.actions;
const __TURBOPACK__default__export__ = pipelineSlice.reducer;
}),
"[project]/lib/store/slices/monitoringSlice.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Monitoring Redux slice
 */ __turbopack_context__.s([
    "addMonitoringMetric",
    ()=>addMonitoringMetric,
    "addReplicationEvent",
    ()=>addReplicationEvent,
    "clearError",
    ()=>clearError,
    "clearEvents",
    ()=>clearEvents,
    "default",
    ()=>__TURBOPACK__default__export__,
    "fetchMonitoringMetrics",
    ()=>fetchMonitoringMetrics,
    "fetchReplicationEvents",
    ()=>fetchReplicationEvents,
    "setRealTimeEnabled",
    ()=>setRealTimeEnabled,
    "setSelectedPipeline",
    ()=>setSelectedPipeline
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/@reduxjs/toolkit/dist/redux-toolkit.modern.mjs [app-ssr] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api/client.ts [app-ssr] (ecmascript)");
;
;
const initialState = {
    events: [],
    metrics: [],
    selectedPipelineId: null,
    isLoading: false,
    error: null,
    realTimeEnabled: false
};
const fetchReplicationEvents = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('monitoring/fetchEvents', async ({ pipelineId, skip, limit, todayOnly, startDate, endDate, tableName })=>{
    return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].getReplicationEvents(pipelineId, skip, limit, todayOnly || false, startDate, endDate, tableName);
});
const fetchMonitoringMetrics = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('monitoring/fetchMetrics', async ({ pipelineId, startTime, endTime })=>{
    // Convert to string if it's a number, or use as-is if it's already a string
    const id = typeof pipelineId === 'number' && !isNaN(pipelineId) ? pipelineId : String(pipelineId);
    // Don't proceed if ID is invalid
    if (!id || id === 'NaN' || id === 'undefined') {
        throw new Error('Invalid pipeline ID');
    }
    return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].getMonitoringMetrics(id, startTime, endTime);
});
const monitoringSlice = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createSlice"])({
    name: 'monitoring',
    initialState,
    reducers: {
        setSelectedPipeline: (state, action)=>{
            state.selectedPipelineId = action.payload;
        },
        addReplicationEvent: (state, action)=>{
            // Check if event already exists (avoid duplicates)
            const existingIndex = state.events.findIndex((e)=>e.id === action.payload.id);
            if (existingIndex === -1) {
                state.events.unshift(action.payload);
                // Keep only last 1000 events
                if (state.events.length > 1000) {
                    state.events = state.events.slice(0, 1000);
                }
            }
        },
        addMonitoringMetric: (state, action)=>{
            state.metrics.push(action.payload);
            // Keep only last 1000 metrics
            if (state.metrics.length > 1000) {
                state.metrics = state.metrics.slice(0, 1000);
            }
        },
        setRealTimeEnabled: (state, action)=>{
            state.realTimeEnabled = action.payload;
        },
        clearEvents: (state)=>{
            state.events = [];
        },
        clearError: (state)=>{
            state.error = null;
        }
    },
    extraReducers: (builder)=>{
        builder.addCase(fetchReplicationEvents.pending, (state)=>{
            state.isLoading = true;
            state.error = null;
        }).addCase(fetchReplicationEvents.fulfilled, (state, action)=>{
            state.isLoading = false;
            // Ensure events is always an array
            state.events = Array.isArray(action.payload) ? action.payload : [];
        }).addCase(fetchReplicationEvents.rejected, (state, action)=>{
            state.isLoading = false;
            state.error = action.error.message || 'Failed to fetch events';
            // Ensure events remains an array even on error
            if (!Array.isArray(state.events)) {
                state.events = [];
            }
        }).addCase(fetchMonitoringMetrics.pending, (state)=>{
            state.isLoading = true;
        }).addCase(fetchMonitoringMetrics.fulfilled, (state, action)=>{
            state.isLoading = false;
            // Ensure metrics is always an array
            state.metrics = Array.isArray(action.payload) ? action.payload : [];
        }).addCase(fetchMonitoringMetrics.rejected, (state, action)=>{
            state.isLoading = false;
            state.error = action.error.message || 'Failed to fetch metrics';
            // Ensure metrics remains an array even on error
            if (!Array.isArray(state.metrics)) {
                state.metrics = [];
            }
        });
    }
});
const { setSelectedPipeline, addReplicationEvent, addMonitoringMetric, setRealTimeEnabled, clearEvents, clearError } = monitoringSlice.actions;
const __TURBOPACK__default__export__ = monitoringSlice.reducer;
}),
"[project]/lib/store/slices/userSlice.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "clearError",
    ()=>clearError,
    "createUser",
    ()=>createUser,
    "default",
    ()=>__TURBOPACK__default__export__,
    "deleteUser",
    ()=>deleteUser,
    "fetchUsers",
    ()=>fetchUsers,
    "setSelectedUser",
    ()=>setSelectedUser,
    "updateUser",
    ()=>updateUser
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/@reduxjs/toolkit/dist/redux-toolkit.modern.mjs [app-ssr] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api/client.ts [app-ssr] (ecmascript)");
;
;
const initialState = {
    users: [],
    selectedUser: null,
    isLoading: false,
    error: null
};
const fetchUsers = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('users/fetchUsers', async ()=>{
    const response = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].client.get('/api/v1/users');
    return response.data;
});
const createUser = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('users/createUser', async (userData)=>{
    const response = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].client.post('/api/v1/users', userData);
    return response.data;
});
const updateUser = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('users/updateUser', async ({ id, userData })=>{
    const response = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].client.put(`/api/v1/users/${id}`, userData);
    return response.data;
});
const deleteUser = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('users/deleteUser', async (id)=>{
    await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["apiClient"].client.delete(`/api/v1/users/${id}`);
    return id;
});
const userSlice = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createSlice"])({
    name: 'users',
    initialState,
    reducers: {
        setSelectedUser: (state, action)=>{
            state.selectedUser = action.payload;
        },
        clearError: (state)=>{
            state.error = null;
        }
    },
    extraReducers: (builder)=>{
        builder// Fetch users
        .addCase(fetchUsers.pending, (state)=>{
            state.isLoading = true;
            state.error = null;
        }).addCase(fetchUsers.fulfilled, (state, action)=>{
            state.isLoading = false;
            state.users = Array.isArray(action.payload) ? action.payload : [];
        }).addCase(fetchUsers.rejected, (state, action)=>{
            state.isLoading = false;
            state.error = action.error.message || 'Failed to fetch users';
        })// Create user
        .addCase(createUser.fulfilled, (state, action)=>{
            state.users.push(action.payload);
        }).addCase(createUser.rejected, (state, action)=>{
            state.error = action.error.message || 'Failed to create user';
        })// Update user
        .addCase(updateUser.fulfilled, (state, action)=>{
            const index = state.users.findIndex((u)=>u.id === action.payload.id);
            if (index !== -1) {
                state.users[index] = action.payload;
            }
        }).addCase(updateUser.rejected, (state, action)=>{
            state.error = action.error.message || 'Failed to update user';
        })// Delete user
        .addCase(deleteUser.fulfilled, (state, action)=>{
            state.users = state.users.filter((u)=>u.id !== action.payload);
        }).addCase(deleteUser.rejected, (state, action)=>{
            state.error = action.error.message || 'Failed to delete user';
        });
    }
});
const { setSelectedUser, clearError } = userSlice.actions;
const __TURBOPACK__default__export__ = userSlice.reducer;
}),
"[project]/lib/store/store.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Redux store configuration
 */ __turbopack_context__.s([
    "store",
    ()=>store
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/@reduxjs/toolkit/dist/redux-toolkit.modern.mjs [app-ssr] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$authSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/authSlice.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$connectionSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/connectionSlice.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$pipelineSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/pipelineSlice.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$monitoringSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/monitoringSlice.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/alertsSlice.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$permissionSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/permissionSlice.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$userSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/userSlice.ts [app-ssr] (ecmascript)");
;
;
;
;
;
;
;
;
const store = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["configureStore"])({
    reducer: {
        auth: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$authSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"],
        connections: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$connectionSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"],
        pipelines: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$pipelineSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"],
        monitoring: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$monitoringSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"],
        alerts: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"],
        permissions: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$permissionSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"],
        users: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$userSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"]
    }
});
}),
"[externals]/child_process [external] (child_process, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("child_process", () => require("child_process"));

module.exports = mod;
}),
"[externals]/buffer [external] (buffer, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("buffer", () => require("buffer"));

module.exports = mod;
}),
"[externals]/net [external] (net, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("net", () => require("net"));

module.exports = mod;
}),
"[externals]/tls [external] (tls, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("tls", () => require("tls"));

module.exports = mod;
}),
"[project]/lib/websocket/client.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * WebSocket client for real-time monitoring
 */ __turbopack_context__.s([
    "wsClient",
    ()=>wsClient
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$socket$2e$io$2d$client$2f$build$2f$esm$2d$debug$2f$index$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/socket.io-client/build/esm-debug/index.js [app-ssr] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/store.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$monitoringSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/monitoringSlice.ts [app-ssr] (ecmascript)");
;
;
;
const WS_URL = ("TURBOPACK compile-time value", "http://localhost:8000") || 'http://localhost:8000';
const WS_ENABLED = process.env.NEXT_PUBLIC_WS_ENABLED !== 'false'; // Default to true unless explicitly disabled
class WebSocketClient {
    socket = null;
    subscribedPipelines = new Set();
    isConnecting = false;
    connectionFailed = false;
    errorCount = 0;
    maxErrorCount = 3;
    statusListeners = new Set();
    connect() {
        // Check if WebSocket is enabled
        if (!WS_ENABLED) {
            console.log('[WebSocket] WebSocket is disabled via configuration');
            this.connectionFailed = true;
            return;
        }
        // If connection has permanently failed, don't retry automatically
        // User can still manually retry via retryConnection()
        if (this.connectionFailed && this.errorCount >= 5) {
            console.log('[WebSocket] Connection permanently failed. Use retryConnection() to manually retry.');
            return;
        }
        // Prevent multiple connection attempts
        if (this.socket?.connected) {
            console.log('[WebSocket] Already connected');
            return;
        }
        if (this.isConnecting) {
            console.log('[WebSocket] Connection already in progress');
            return;
        }
        // Reset failed state to allow retry (if error count is low)
        if (this.connectionFailed && this.errorCount < 5) {
            console.log('[WebSocket] Resetting failed state and attempting reconnection');
            this.connectionFailed = false;
            // Clean up old socket if exists
            if (this.socket) {
                this.socket.removeAllListeners();
                this.socket.disconnect();
                this.socket = null;
            }
        }
        this.isConnecting = true;
        console.log('[WebSocket] Attempting to connect to:', WS_URL);
        this.socket = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$socket$2e$io$2d$client$2f$build$2f$esm$2d$debug$2f$index$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["io"])(WS_URL, {
            path: '/socket.io',
            transports: [
                'polling',
                'websocket'
            ],
            reconnection: this.errorCount < 3,
            reconnectionDelay: 2000,
            reconnectionDelayMax: 10000,
            reconnectionAttempts: 2,
            timeout: 10000,
            forceNew: false,
            autoConnect: true,
            // Suppress default error logging
            withCredentials: false
        });
        this.socket.on('connect', ()=>{
            console.log('========================================');
            console.log('[Frontend] WEBSOCKET CONNECTED');
            console.log('========================================');
            console.log('[Frontend] Socket ID:', this.socket?.id);
            console.log('[Frontend] Previously subscribed pipelines:', Array.from(this.subscribedPipelines));
            this.isConnecting = false;
            this.connectionFailed = false; // Reset failure flag on successful connection
            this.errorCount = 0; // Reset error count on successful connection
            // Notify all listeners about status change
            this.notifyStatusListeners();
            // Re-subscribe to previously subscribed pipelines
            this.subscribedPipelines.forEach((pipelineId)=>{
                if (this.socket?.connected) {
                    console.log(`[Frontend] Re-subscribing to pipeline: ${pipelineId}`);
                    this.socket.emit('subscribe_pipeline', {
                        pipeline_id: pipelineId
                    });
                }
            });
            console.log('========================================');
        });
        this.socket.on('disconnect', (reason)=>{
            console.log('WebSocket disconnected:', reason);
            this.isConnecting = false;
            // Notify all listeners about status change
            this.notifyStatusListeners();
            if (reason === 'io server disconnect') {
                // Server disconnected, try to reconnect manually
                this.socket?.connect();
            }
        });
        this.socket.on('connect_error', (error)=>{
            this.errorCount++;
            this.isConnecting = false;
            // Only log first few errors to avoid console spam
            if (this.errorCount <= this.maxErrorCount) {
                console.warn(`[WebSocket] Connection error (${this.errorCount}/${this.maxErrorCount}):`, error.message);
                if (this.errorCount === this.maxErrorCount) {
                    console.warn('[WebSocket] Suppressing further connection errors. Backend may not have Socket.IO configured.');
                }
            }
            // If we've had multiple errors quickly, mark as failed to stop retries
            // This prevents infinite retry loops when backend doesn't support WebSocket
            if (this.errorCount >= 3) {
                this.connectionFailed = true;
                if (this.socket) {
                    this.socket.io.reconnecting = false;
                    this.socket.disconnect();
                    this.socket = null; // Clean up socket to prevent further attempts
                }
                console.warn('[WebSocket] Stopped connection attempts. Backend does not appear to support WebSocket. Using polling mode.');
            }
        });
        this.socket.on('reconnect_attempt', (attemptNumber)=>{
            // Only log first few attempts to avoid spam
            if (attemptNumber <= 2) {
                console.log(`[WebSocket] Reconnection attempt ${attemptNumber}`);
            }
        });
        this.socket.on('reconnect_failed', ()=>{
            if (this.errorCount <= this.maxErrorCount) {
                console.warn('[WebSocket] All reconnection attempts failed. WebSocket unavailable. Using polling mode.');
            }
            this.connectionFailed = true;
            this.isConnecting = false;
            // Stop reconnection attempts
            if (this.socket) {
                this.socket.io.reconnecting = false;
            }
        });
        this.socket.on('reconnect', (attemptNumber)=>{
            console.log(`[WebSocket] Successfully reconnected after ${attemptNumber} attempts`);
            this.connectionFailed = false;
            this.isConnecting = false;
            this.errorCount = 0; // Reset error count on reconnect
            // Notify all listeners about status change
            this.notifyStatusListeners();
            // Re-subscribe to all previously subscribed pipelines
            this.subscribedPipelines.forEach((pipelineId)=>{
                if (this.socket?.connected) {
                    console.log(`[WebSocket] Re-subscribing to pipeline: ${pipelineId}`);
                    this.socket.emit('subscribe_pipeline', {
                        pipeline_id: pipelineId
                    });
                }
            });
        });
        this.socket.on('error', (error)=>{
            // Suppress WebSocket errors - backend may not have Socket.IO configured
            // This is not critical for the application to function
            // Disable reconnection to prevent spam
            if (this.socket) {
                this.socket.io.reconnecting = false;
            }
        // Don't log to console to avoid cluttering logs
        });
        this.socket.on('replication_event', (data)=>{
            try {
                console.log('========================================');
                console.log('[Frontend] RECEIVED REPLICATION EVENT');
                console.log('========================================');
                console.log('[Frontend] Event ID:', data.id);
                console.log('[Frontend] Pipeline ID:', data.pipeline_id);
                console.log('[Frontend] Event Type:', data.event_type);
                console.log('[Frontend] Table:', data.table_name);
                console.log('[Frontend] Status:', data.status);
                console.log('[Frontend] Full event data:', data);
                console.log('========================================');
                __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["store"].dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$monitoringSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["addReplicationEvent"])(data));
                console.log('[Frontend] ✓ Event added to Redux store');
                // Refresh events from API with correct parameters when new event is received
                // This ensures the events list is up-to-date with all parameters applied
                const state = __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["store"].getState();
                const monitoringState = state.monitoring;
                const selectedPipelineId = monitoringState.selectedPipelineId;
                // Prepare fetch parameters based on current state
                const fetchParams = {
                    limit: 500,
                    todayOnly: false
                };
                // Add pipeline_id if a specific pipeline is selected, or use the event's pipeline_id
                if (selectedPipelineId) {
                    fetchParams.pipelineId = selectedPipelineId;
                } else if (data.pipeline_id) {
                    // If no pipeline is selected but event has pipeline_id, refresh with that pipeline
                    fetchParams.pipelineId = data.pipeline_id;
                }
                // Dispatch fetch to refresh events list with correct parameters
                __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["store"].dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$monitoringSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["fetchReplicationEvents"])(fetchParams));
                // Show browser notification for new events
                if (("TURBOPACK compile-time value", "undefined") !== 'undefined' && 'Notification' in window && Notification.permission === 'granted') //TURBOPACK unreachable
                ;
            } catch (error) {
                console.error('Error handling replication event:', error);
            }
        });
        this.socket.on('monitoring_metric', (data)=>{
            try {
                console.log('Received monitoring metric:', data);
                __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["store"].dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$monitoringSlice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["addMonitoringMetric"])(data));
            } catch (error) {
                console.error('Error handling monitoring metric:', error);
            }
        });
        this.socket.on('pipeline_status', (data)=>{
            try {
                console.log('Pipeline status update:', data);
            // Handle pipeline status updates
            } catch (error) {
                console.error('Error handling pipeline status:', error);
            }
        });
    }
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
            this.subscribedPipelines.clear();
            this.isConnecting = false;
        }
    }
    subscribePipeline(pipelineId) {
        // Validate pipeline ID
        if (!pipelineId || pipelineId === 'NaN' || pipelineId === 'undefined' || typeof pipelineId === 'number' && (isNaN(pipelineId) || !isFinite(pipelineId))) {
            console.error(`[Frontend] ✗ Invalid pipeline ID for subscription: ${pipelineId}`);
            return;
        }
        // Skip if already subscribed
        if (this.subscribedPipelines.has(pipelineId)) {
            console.log(`[Frontend] Already subscribed to pipeline: ${pipelineId}`);
            return;
        }
        console.log(`[Frontend] ========================================`);
        console.log(`[Frontend] SUBSCRIBING TO PIPELINE`);
        console.log(`[Frontend] ========================================`);
        console.log(`[Frontend] Pipeline ID: ${pipelineId} (type: ${typeof pipelineId})`);
        console.log(`[Frontend] WebSocket connected: ${this.socket?.connected || false}`);
        console.log(`[Frontend] Socket ID: ${this.socket?.id || 'N/A'}`);
        // Add to set first to prevent duplicate subscriptions
        this.subscribedPipelines.add(pipelineId);
        if (!this.socket?.connected) {
            console.log(`[Frontend] WebSocket not connected, connecting...`);
            this.connect();
            // Wait for connection before subscribing
            if (this.socket) {
                this.socket.once('connect', ()=>{
                    if (this.socket?.connected) {
                        console.log(`[Frontend] WebSocket connected, subscribing to pipeline: ${pipelineId}`);
                        this.socket.emit('subscribe_pipeline', {
                            pipeline_id: pipelineId
                        });
                        console.log(`[Frontend] ✓ Subscription request sent for pipeline: ${pipelineId}`);
                    }
                });
            }
        } else if (this.socket.connected) {
            // Already connected, subscribe immediately
            console.log(`[Frontend] WebSocket already connected, subscribing immediately`);
            this.socket.emit('subscribe_pipeline', {
                pipeline_id: pipelineId
            });
            console.log(`[Frontend] ✓ Subscription request sent for pipeline: ${pipelineId}`);
        }
        console.log(`[Frontend] ========================================`);
    }
    unsubscribePipeline(pipelineId) {
        if (this.socket && this.subscribedPipelines.has(pipelineId)) {
            this.socket.emit('unsubscribe_pipeline', {
                pipeline_id: pipelineId
            });
            this.subscribedPipelines.delete(pipelineId);
        }
    }
    isConnected() {
        // Check actual connection state - if socket is connected, always return true
        return this.socket?.connected === true;
    }
    isAvailable() {
        // WebSocket is available if:
        // 1. It's connected (always available if connected, regardless of connectionFailed flag)
        // 2. It's still trying to connect (isConnecting)
        // 3. Socket exists and hasn't permanently failed (for initial connection attempts)
        // Priority: connected > connecting > not failed
        if (this.socket?.connected === true) {
            return true; // Always available if connected
        }
        if (this.isConnecting) {
            return true; // Available if connecting
        }
        // If not connected and not connecting, only available if not permanently failed
        return !this.connectionFailed && this.socket !== null;
    }
    reset() {
        // Reset connection state to allow retry
        console.log('[WebSocket] Resetting connection state');
        this.connectionFailed = false;
        this.isConnecting = false;
        this.errorCount = 0; // Reset error count
        if (this.socket) {
            this.socket.removeAllListeners();
            this.socket.disconnect();
            this.socket = null;
        }
    }
    retryConnection() {
        // Manually trigger reconnection
        console.log('[WebSocket] Manual reconnection requested');
        this.reset();
        // Check if WebSocket is enabled
        if (!WS_ENABLED) {
            console.warn('[WebSocket] WebSocket is disabled via configuration. Enable it in environment variables.');
            this.connectionFailed = true;
            return;
        }
        this.connect();
    }
    disable() {
        // Manually disable WebSocket (useful for testing or when backend doesn't support it)
        console.log('[WebSocket] Manually disabling WebSocket');
        this.connectionFailed = true;
        this.isConnecting = false;
        if (this.socket) {
            this.socket.io.reconnecting = false;
            this.socket.removeAllListeners();
            this.socket.disconnect();
            this.socket = null;
        }
    }
    isDisabled() {
        // Check if WebSocket is disabled or permanently failed
        return !WS_ENABLED || this.connectionFailed && this.errorCount >= 3;
    }
    hasFailed() {
        // Check if WebSocket connection has permanently failed (backend doesn't support Socket.IO)
        return this.connectionFailed;
    }
    // Status change notification system
    onStatusChange(callback) {
        // Add listener
        this.statusListeners.add(callback);
        // Return unsubscribe function
        return ()=>{
            this.statusListeners.delete(callback);
        };
    }
    notifyStatusListeners() {
        // Notify all listeners about status change
        this.statusListeners.forEach((listener)=>{
            try {
                listener();
            } catch (error) {
                console.error('Error in status listener:', error);
            }
        });
    }
}
const wsClient = new WebSocketClient();
}),
"[project]/components/providers/ReduxProvider.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Redux Provider component
 */ __turbopack_context__.s([
    "ReduxProvider",
    ()=>ReduxProvider
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$redux$2f$dist$2f$react$2d$redux$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/react-redux/dist/react-redux.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/store.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$websocket$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/websocket/client.ts [app-ssr] (ecmascript)");
'use client';
;
;
;
;
;
function ReduxProvider({ children }) {
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        // Connect WebSocket on mount
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$websocket$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["wsClient"].connect();
        // Cleanup on unmount
        return ()=>{
            __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$websocket$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["wsClient"].disconnect();
        };
    }, []);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$redux$2f$dist$2f$react$2d$redux$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Provider"], {
        store: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["store"],
        children: children
    }, void 0, false, {
        fileName: "[project]/components/providers/ReduxProvider.tsx",
        lineNumber: 22,
        columnNumber: 10
    }, this);
}
}),
"[project]/components/ui/use-toast.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "reducer",
    ()=>reducer,
    "toast",
    ()=>toast,
    "useToast",
    ()=>useToast
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
"use client";
;
const TOAST_LIMIT = 3;
const TOAST_REMOVE_DELAY = 5000;
const actionTypes = {
    ADD_TOAST: "ADD_TOAST",
    UPDATE_TOAST: "UPDATE_TOAST",
    DISMISS_TOAST: "DISMISS_TOAST",
    REMOVE_TOAST: "REMOVE_TOAST"
};
let count = 0;
function genId() {
    count = (count + 1) % Number.MAX_VALUE;
    return count.toString();
}
const toastTimeouts = new Map();
const addToRemoveQueue = (toastId)=>{
    if (toastTimeouts.has(toastId)) {
        return;
    }
    const timeout = setTimeout(()=>{
        toastTimeouts.delete(toastId);
        dispatch({
            type: "REMOVE_TOAST",
            toastId: toastId
        });
    }, TOAST_REMOVE_DELAY);
    toastTimeouts.set(toastId, timeout);
};
const reducer = (state, action)=>{
    switch(action.type){
        case "ADD_TOAST":
            return {
                ...state,
                toasts: [
                    action.toast,
                    ...state.toasts
                ].slice(0, TOAST_LIMIT)
            };
        case "UPDATE_TOAST":
            return {
                ...state,
                toasts: state.toasts.map((t)=>t.id === action.toast.id ? {
                        ...t,
                        ...action.toast
                    } : t)
            };
        case "DISMISS_TOAST":
            {
                const { toastId } = action;
                if (toastId) {
                    addToRemoveQueue(toastId);
                } else {
                    state.toasts.forEach((toast)=>{
                        if (toast.id) addToRemoveQueue(toast.id);
                    });
                }
                return {
                    ...state,
                    toasts: state.toasts.map((t)=>t.id === toastId || toastId === undefined ? {
                            ...t,
                            open: false
                        } : t)
                };
            }
        case "REMOVE_TOAST":
            if (action.toastId === undefined) {
                return {
                    ...state,
                    toasts: []
                };
            }
            return {
                ...state,
                toasts: state.toasts.filter((t)=>t.id !== action.toastId)
            };
    }
};
const listeners = [];
let memoryState = {
    toasts: []
};
function dispatch(action) {
    memoryState = reducer(memoryState, action);
    listeners.forEach((listener)=>{
        listener(memoryState);
    });
}
function toast({ ...props }) {
    const id = genId();
    const update = (props)=>dispatch({
            type: "UPDATE_TOAST",
            toast: {
                ...props,
                id
            }
        });
    const dismiss = ()=>dispatch({
            type: "DISMISS_TOAST",
            toastId: id
        });
    dispatch({
        type: "ADD_TOAST",
        toast: {
            ...props,
            id,
            open: true,
            onOpenChange: (open)=>{
                if (!open) dismiss();
            }
        }
    });
    return {
        id: id,
        dismiss,
        update
    };
}
function useToast() {
    const [state, setState] = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"](memoryState);
    __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"](()=>{
        listeners.push(setState);
        return ()=>{
            const index = listeners.indexOf(setState);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        };
    }, [
        state
    ]);
    return {
        ...state,
        toast,
        dismiss: (toastId)=>dispatch({
                type: "DISMISS_TOAST",
                toastId
            })
    };
}
;
}),
"[project]/components/ui/toaster.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "Toaster",
    ()=>Toaster
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$use$2d$toast$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/ui/use-toast.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/x.js [app-ssr] (ecmascript) <export default as X>");
"use client";
;
;
;
function Toaster() {
    const { toasts } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$use$2d$toast$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useToast"])();
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "fixed top-0 right-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:top-auto sm:right-0 sm:bottom-0 sm:flex-col md:max-w-[420px] pointer-events-none",
        children: toasts.map(function({ id, title, description, variant, ...props }) {
            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "pointer-events-auto mb-4 flex w-full flex-col items-start gap-2 overflow-hidden rounded-lg border p-4 shadow-lg transition-all data-[swipe=cancel]:translate-x-0 data-[swipe=end]:translate-x-[var(--radix-toast-swipe-end-x)] data-[swipe=move]:translate-x-[var(--radix-toast-swipe-move-x)] data-[swipe=move]:transition-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[swipe=end]:animate-out data-[state=closed]:fade-out-80 data-[state=closed]:slide-out-to-right-full data-[state=open]:slide-in-from-top-full data-[state=open]:sm:slide-in-from-bottom-full",
                style: {
                    backgroundColor: variant === "destructive" ? "rgba(239, 68, 68, 0.1)" : "rgba(6, 182, 212, 0.1)",
                    borderColor: variant === "destructive" ? "rgba(239, 68, 68, 0.3)" : "rgba(6, 182, 212, 0.3)"
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "grid gap-1 flex-1",
                        children: [
                            title && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "text-sm font-semibold",
                                style: {
                                    color: variant === "destructive" ? "#ef4444" : "#06b6d4"
                                },
                                children: title
                            }, void 0, false, {
                                fileName: "[project]/components/ui/toaster.tsx",
                                lineNumber: 23,
                                columnNumber: 33
                            }, this),
                            description && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "text-sm opacity-90 text-foreground-muted",
                                children: description
                            }, void 0, false, {
                                fileName: "[project]/components/ui/toaster.tsx",
                                lineNumber: 28,
                                columnNumber: 33
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/ui/toaster.tsx",
                        lineNumber: 21,
                        columnNumber: 25
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        onClick: ()=>{
                        // Auto-dismiss after showing
                        },
                        className: "absolute right-2 top-2 rounded-md p-1 opacity-70 transition-opacity hover:opacity-100",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                            className: "h-4 w-4"
                        }, void 0, false, {
                            fileName: "[project]/components/ui/toaster.tsx",
                            lineNumber: 39,
                            columnNumber: 29
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/ui/toaster.tsx",
                        lineNumber: 33,
                        columnNumber: 25
                    }, this)
                ]
            }, id, true, {
                fileName: "[project]/components/ui/toaster.tsx",
                lineNumber: 13,
                columnNumber: 21
            }, this);
        })
    }, void 0, false, {
        fileName: "[project]/components/ui/toaster.tsx",
        lineNumber: 10,
        columnNumber: 9
    }, this);
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__5bfb625f._.js.map