(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/lib/utils.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "cn",
    ()=>cn
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/clsx/dist/clsx.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$tailwind$2d$merge$2f$dist$2f$bundle$2d$mjs$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/tailwind-merge/dist/bundle-mjs.mjs [app-client] (ecmascript)");
;
;
function cn(...inputs) {
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$tailwind$2d$merge$2f$dist$2f$bundle$2d$mjs$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["twMerge"])((0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["clsx"])(inputs));
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/contexts/sidebar-context.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "SidebarProvider",
    ()=>SidebarProvider,
    "useSidebar",
    ()=>useSidebar
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature(), _s1 = __turbopack_context__.k.signature();
"use client";
;
const SidebarContext = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["createContext"])(undefined);
function SidebarProvider({ children }) {
    _s();
    const [isCollapsed, setIsCollapsed] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [mounted, setMounted] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "SidebarProvider.useEffect": ()=>{
            const stored = localStorage.getItem("sidebarCollapsed") === "true";
            setIsCollapsed(stored);
            setMounted(true);
        }
    }["SidebarProvider.useEffect"], []);
    const toggleCollapse = ()=>{
        setIsCollapsed((prev)=>{
            const newState = !prev;
            localStorage.setItem("sidebarCollapsed", String(newState));
            return newState;
        });
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(SidebarContext.Provider, {
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
_s(SidebarProvider, "nSl/EcD0fHk+qyL7EJdtbOpaE2s=");
_c = SidebarProvider;
function useSidebar() {
    _s1();
    const context = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useContext"])(SidebarContext);
    if (context === undefined) {
        throw new Error("useSidebar must be used within SidebarProvider");
    }
    return context;
}
_s1(useSidebar, "b9L3QQ+jgeyIrH0NfHrJ8nn7VMU=");
var _c;
__turbopack_context__.k.register(_c, "SidebarProvider");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/layout/sidebar.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "Sidebar",
    ()=>Sidebar
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/client/app-dir/link.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/utils.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$database$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Database$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/database.js [app-client] (ecmascript) <export default as Database>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chart$2d$column$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__BarChart3$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chart-column.js [app-client] (ecmascript) <export default as BarChart3>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/settings.js [app-client] (ecmascript) <export default as Settings>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$branch$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__GitBranch$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/git-branch.js [app-client] (ecmascript) <export default as GitBranch>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__AlertTriangle$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/triangle-alert.js [app-client] (ecmascript) <export default as AlertTriangle>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$activity$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Activity$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/activity.js [app-client] (ecmascript) <export default as Activity>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$house$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Home$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/house.js [app-client] (ecmascript) <export default as Home>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$shield$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Shield$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/shield.js [app-client] (ecmascript) <export default as Shield>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$users$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Users$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/users.js [app-client] (ecmascript) <export default as Users>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$left$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronLeft$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-left.js [app-client] (ecmascript) <export default as ChevronLeft>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$right$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronRight$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-right.js [app-client] (ecmascript) <export default as ChevronRight>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-down.js [app-client] (ecmascript) <export default as ChevronDown>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$up$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronUp$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-up.js [app-client] (ecmascript) <export default as ChevronUp>");
var __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$sidebar$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/contexts/sidebar-context.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
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
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$house$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Home$3e$__["Home"]
            },
            {
                href: "/monitoring",
                label: "Monitoring",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$activity$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Activity$3e$__["Activity"]
            }
        ]
    },
    {
        title: "REPLICATION",
        items: [
            {
                href: "/connections",
                label: "Connections",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$database$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Database$3e$__["Database"]
            },
            {
                href: "/pipelines",
                label: "Pipelines",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$branch$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__GitBranch$3e$__["GitBranch"]
            },
            {
                href: "/analytics",
                label: "Analytics",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chart$2d$column$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__BarChart3$3e$__["BarChart3"]
            }
        ]
    },
    {
        title: "OPERATIONS",
        items: [
            {
                href: "/errors",
                label: "Errors & Alerts",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__AlertTriangle$3e$__["AlertTriangle"]
            },
            {
                href: "/governance",
                label: "Data Governance",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$shield$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Shield$3e$__["Shield"]
            },
            {
                href: "/users",
                label: "User Management",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$users$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Users$3e$__["Users"]
            },
            {
                href: "/settings",
                label: "Settings",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__["Settings"]
            }
        ]
    }
];
function Sidebar() {
    _s();
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["usePathname"])();
    const { isCollapsed, toggleCollapse, mounted } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$sidebar$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useSidebar"])();
    const [expandedSections, setExpandedSections] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        PLATFORM: true,
        REPLICATION: true,
        OPERATIONS: true
    });
    // Auto-expand section if current path matches any item in that section
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "Sidebar.useEffect": ()=>{
            if (!isCollapsed) {
                const newExpanded = {};
                menuSections.forEach({
                    "Sidebar.useEffect": (section)=>{
                        const hasActiveItem = section.items.some({
                            "Sidebar.useEffect.hasActiveItem": (item)=>pathname === item.href || pathname.startsWith(item.href + "/")
                        }["Sidebar.useEffect.hasActiveItem"]);
                        newExpanded[section.title] = hasActiveItem || expandedSections[section.title];
                    }
                }["Sidebar.useEffect"]);
                setExpandedSections(newExpanded);
            }
        }
    }["Sidebar.useEffect"], [
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
    if (!mounted) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("aside", {
            className: "w-64 border-r border-border bg-sidebar flex flex-col transition-all duration-300",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "p-6 border-b border-border"
            }, void 0, false, {
                fileName: "[project]/components/layout/sidebar.tsx",
                lineNumber: 85,
                columnNumber: 9
            }, this)
        }, void 0, false, {
            fileName: "[project]/components/layout/sidebar.tsx",
            lineNumber: 84,
            columnNumber: 7
        }, this);
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("aside", {
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["cn"])("border-r border-border bg-sidebar flex flex-col transition-all duration-300", isCollapsed ? "w-20" : "w-64"),
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "p-6 border-b border-border flex items-center justify-between",
                children: [
                    !isCollapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex items-center gap-2",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "w-8 h-8 bg-gradient-to-br from-primary to-info rounded-lg flex items-center justify-center flex-shrink-0",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$database$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Database$3e$__["Database"], {
                                    className: "w-5 h-5 text-foreground"
                                }, void 0, false, {
                                    fileName: "[project]/components/layout/sidebar.tsx",
                                    lineNumber: 102,
                                    columnNumber: 15
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/components/layout/sidebar.tsx",
                                lineNumber: 101,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                                        className: "font-bold text-foreground text-sm",
                                        children: "CDC Admin"
                                    }, void 0, false, {
                                        fileName: "[project]/components/layout/sidebar.tsx",
                                        lineNumber: 105,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        className: "text-xs text-foreground-muted",
                                        children: "Platform"
                                    }, void 0, false, {
                                        fileName: "[project]/components/layout/sidebar.tsx",
                                        lineNumber: 106,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/layout/sidebar.tsx",
                                lineNumber: 104,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/layout/sidebar.tsx",
                        lineNumber: 100,
                        columnNumber: 11
                    }, this),
                    isCollapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "w-8 h-8 bg-gradient-to-br from-primary to-info rounded-lg flex items-center justify-center",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$database$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Database$3e$__["Database"], {
                            className: "w-5 h-5 text-foreground"
                        }, void 0, false, {
                            fileName: "[project]/components/layout/sidebar.tsx",
                            lineNumber: 112,
                            columnNumber: 13
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/layout/sidebar.tsx",
                        lineNumber: 111,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        onClick: toggleCollapse,
                        className: "p-1.5 hover:bg-surface-hover rounded-lg transition-colors",
                        "aria-label": "Toggle sidebar",
                        children: isCollapsed ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$right$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronRight$3e$__["ChevronRight"], {
                            className: "w-4 h-4"
                        }, void 0, false, {
                            fileName: "[project]/components/layout/sidebar.tsx",
                            lineNumber: 120,
                            columnNumber: 26
                        }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$left$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronLeft$3e$__["ChevronLeft"], {
                            className: "w-4 h-4"
                        }, void 0, false, {
                            fileName: "[project]/components/layout/sidebar.tsx",
                            lineNumber: 120,
                            columnNumber: 65
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/layout/sidebar.tsx",
                        lineNumber: 115,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/layout/sidebar.tsx",
                lineNumber: 98,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("nav", {
                className: "flex-1 overflow-y-auto px-3 py-4 space-y-6",
                children: menuSections.map((section)=>{
                    const isExpanded = expandedSections[section.title] ?? true;
                    const hasActiveItem = section.items.some((item)=>pathname === item.href || pathname.startsWith(item.href + "/"));
                    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        children: !isCollapsed ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    onClick: ()=>toggleSection(section.title),
                                    className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["cn"])("w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold text-foreground-muted uppercase tracking-wider mb-2 transition-colors hover:bg-surface-hover hover:text-primary", hasActiveItem && "text-primary"),
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            children: section.title
                                        }, void 0, false, {
                                            fileName: "[project]/components/layout/sidebar.tsx",
                                            lineNumber: 144,
                                            columnNumber: 21
                                        }, this),
                                        isExpanded ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$up$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronUp$3e$__["ChevronUp"], {
                                            className: "w-3 h-3"
                                        }, void 0, false, {
                                            fileName: "[project]/components/layout/sidebar.tsx",
                                            lineNumber: 146,
                                            columnNumber: 23
                                        }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__["ChevronDown"], {
                                            className: "w-3 h-3"
                                        }, void 0, false, {
                                            fileName: "[project]/components/layout/sidebar.tsx",
                                            lineNumber: 148,
                                            columnNumber: 23
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/layout/sidebar.tsx",
                                    lineNumber: 137,
                                    columnNumber: 19
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["cn"])("space-y-1 overflow-hidden transition-all duration-300 ease-in-out", isExpanded ? "max-h-96 opacity-100" : "max-h-0 opacity-0"),
                                    children: section.items.map((item)=>{
                                        const Icon = item.icon;
                                        const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
                                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                                            href: item.href,
                                            className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["cn"])("flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors", isActive ? "bg-primary/20 text-primary border border-primary/30 font-semibold" : "text-foreground-muted hover:text-primary hover:bg-surface-hover"),
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(Icon, {
                                                    className: "w-4 h-4 flex-shrink-0"
                                                }, void 0, false, {
                                                    fileName: "[project]/components/layout/sidebar.tsx",
                                                    lineNumber: 173,
                                                    columnNumber: 27
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                    children: item.label
                                                }, void 0, false, {
                                                    fileName: "[project]/components/layout/sidebar.tsx",
                                                    lineNumber: 174,
                                                    columnNumber: 27
                                                }, this)
                                            ]
                                        }, item.href, true, {
                                            fileName: "[project]/components/layout/sidebar.tsx",
                                            lineNumber: 163,
                                            columnNumber: 25
                                        }, this);
                                    })
                                }, void 0, false, {
                                    fileName: "[project]/components/layout/sidebar.tsx",
                                    lineNumber: 153,
                                    columnNumber: 19
                                }, this)
                            ]
                        }, void 0, true) : /* Collapsed Sidebar - Show all items without dropdown */ /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "space-y-1",
                            children: section.items.map((item)=>{
                                const Icon = item.icon;
                                const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
                                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                                    href: item.href,
                                    title: item.label,
                                    className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["cn"])("flex items-center gap-3 py-2 rounded-lg text-sm font-medium transition-colors justify-center px-0", isActive ? "bg-primary/20 text-primary border border-primary/30 font-semibold" : "text-foreground-muted hover:text-primary hover:bg-surface-hover"),
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(Icon, {
                                        className: "w-4 h-4 flex-shrink-0"
                                    }, void 0, false, {
                                        fileName: "[project]/components/layout/sidebar.tsx",
                                        lineNumber: 198,
                                        columnNumber: 25
                                    }, this)
                                }, item.href, false, {
                                    fileName: "[project]/components/layout/sidebar.tsx",
                                    lineNumber: 187,
                                    columnNumber: 23
                                }, this);
                            })
                        }, void 0, false, {
                            fileName: "[project]/components/layout/sidebar.tsx",
                            lineNumber: 182,
                            columnNumber: 17
                        }, this)
                    }, section.title, false, {
                        fileName: "[project]/components/layout/sidebar.tsx",
                        lineNumber: 133,
                        columnNumber: 13
                    }, this);
                })
            }, void 0, false, {
                fileName: "[project]/components/layout/sidebar.tsx",
                lineNumber: 125,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "p-3 border-t border-border",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["cn"])("glass p-3 rounded-lg text-xs text-foreground-muted", isCollapsed && "flex justify-center"),
                    children: [
                        !isCollapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                    className: "font-semibold mb-1",
                                    children: "v1.0.0"
                                }, void 0, false, {
                                    fileName: "[project]/components/layout/sidebar.tsx",
                                    lineNumber: 214,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                    children: "Real-time CDC Platform"
                                }, void 0, false, {
                                    fileName: "[project]/components/layout/sidebar.tsx",
                                    lineNumber: 215,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true),
                        isCollapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                            className: "font-semibold",
                            children: "v1"
                        }, void 0, false, {
                            fileName: "[project]/components/layout/sidebar.tsx",
                            lineNumber: 218,
                            columnNumber: 27
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/layout/sidebar.tsx",
                    lineNumber: 211,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/components/layout/sidebar.tsx",
                lineNumber: 210,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/layout/sidebar.tsx",
        lineNumber: 91,
        columnNumber: 5
    }, this);
}
_s(Sidebar, "vHynBF6YqfwkHfcvbCuj0umXjME=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["usePathname"],
        __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$sidebar$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useSidebar"]
    ];
});
_c = Sidebar;
var _c;
__turbopack_context__.k.register(_c, "Sidebar");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/contexts/theme-context.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ThemeProvider",
    ()=>ThemeProvider,
    "useTheme",
    ()=>useTheme
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature(), _s1 = __turbopack_context__.k.signature();
"use client";
;
const ThemeContext = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["createContext"])(undefined);
function ThemeProvider({ children }) {
    _s();
    // Start with "dark" as default to match server-side rendering
    // This prevents hydration mismatch
    const [theme, setTheme] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("dark");
    const [mounted, setMounted] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "ThemeProvider.useEffect": ()=>{
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
        }
    }["ThemeProvider.useEffect"], []);
    const toggleTheme = ()=>{
        setTheme((prev)=>{
            const newTheme = prev === "dark" ? "light" : "dark";
            localStorage.setItem("theme", newTheme);
            document.documentElement.classList.toggle("dark", newTheme === "dark");
            document.documentElement.classList.toggle("light", newTheme === "light");
            return newTheme;
        });
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(ThemeContext.Provider, {
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
_s(ThemeProvider, "PMXYpdFteak97Vtku2TV0tPQEaI=");
_c = ThemeProvider;
function useTheme() {
    _s1();
    const context = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useContext"])(ThemeContext);
    if (context === undefined) {
        throw new Error("useTheme must be used within ThemeProvider");
    }
    // Return default theme if not mounted yet to prevent hydration issues
    return {
        theme: context.theme || "dark",
        toggleTheme: context.toggleTheme
    };
}
_s1(useTheme, "b9L3QQ+jgeyIrH0NfHrJ8nn7VMU=");
var _c;
__turbopack_context__.k.register(_c, "ThemeProvider");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/store/hooks.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Typed Redux hooks
 */ __turbopack_context__.s([
    "useAppDispatch",
    ()=>useAppDispatch,
    "useAppSelector",
    ()=>useAppSelector
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$redux$2f$dist$2f$react$2d$redux$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/react-redux/dist/react-redux.mjs [app-client] (ecmascript)");
;
const useAppDispatch = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$redux$2f$dist$2f$react$2d$redux$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useDispatch"].withTypes();
const useAppSelector = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$redux$2f$dist$2f$react$2d$redux$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useSelector"].withTypes();
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/api/client.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * API client for Python backend
 */ __turbopack_context__.s([
    "apiClient",
    ()=>apiClient
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$axios$2f$lib$2f$axios$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/axios/lib/axios.js [app-client] (ecmascript)");
;
const API_BASE_URL = ("TURBOPACK compile-time value", "http://localhost:8000") || 'http://localhost:8000';
class ApiClient {
    client;
    constructor(){
        this.client = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$axios$2f$lib$2f$axios$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"].create({
            baseURL: API_BASE_URL,
            headers: {
                'Content-Type': 'application/json'
            },
            timeout: 10000
        });
        // Add auth token to requests
        this.client.interceptors.request.use((config)=>{
            const token = this.getToken();
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        });
        // Handle auth errors and timeouts
        this.client.interceptors.response.use((response)=>response, (error)=>{
            // Handle timeout errors - but don't log for endpoints with their own retry logic
            if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
                // Don't log for endpoints with retry logic - they handle their own errors silently
                const url = error.config?.url || '';
                const hasRetryLogic = url.includes('/api/v1/connections/') || url.includes('/api/v1/pipelines/') || url.includes('/api/v1/monitoring/');
                // Suppress all timeout logging for endpoints with retry logic
                // Only log in development for endpoints without retry logic
                if (!hasRetryLogic && ("TURBOPACK compile-time value", "development") === 'development') {
                    console.error('Request timeout:', url);
                }
                const timeoutError = new Error('Request timeout: The server took too long to respond. Please try again.');
                timeoutError.isTimeout = true;
                timeoutError.code = 'ECONNABORTED';
                return Promise.reject(timeoutError);
            }
            // Handle network errors - but skip for table data endpoints which have their own error handling
            const url = error.config?.url || error.request?.responseURL || '';
            const isTableDataEndpoint = url.includes('/tables/') && url.includes('/data');
            // Log for debugging
            if ("TURBOPACK compile-time truthy", 1) {
                console.log('[Axios Interceptor] Error caught:', {
                    url,
                    isTableDataEndpoint,
                    errorCode: error.code,
                    errorMessage: error.message,
                    hasResponse: !!error.response,
                    responseStatus: error.response?.status
                });
            }
            // Only handle network errors for non-table-data endpoints
            // Table data endpoints have longer timeouts and better error handling
            if (!isTableDataEndpoint && (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error'))) {
                const networkError = new Error('Cannot connect to server. Please ensure the backend is running on http://localhost:8000');
                networkError.isNetworkError = true;
                return Promise.reject(networkError);
            }
            // For table data endpoints, preserve the original error so getTableData can handle it
            if (isTableDataEndpoint) {
                // Mark network errors but don't transform them - let getTableData handle it
                if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error') || error.code === 'ERR_NETWORK') {
                    error.isNetworkError = true;
                }
                // Don't transform the error - let getTableData handle it with proper error messages
                return Promise.reject(error);
            }
            if (error.response?.status === 401 || error.response?.status === 403) {
                // Clear token and redirect to login for auth errors
                this.clearToken();
                if ("TURBOPACK compile-time truthy", 1) {
                    const currentPath = window.location.pathname;
                    // Only redirect if not already on a login/signup page
                    if (!currentPath.startsWith('/auth/login') && !currentPath.startsWith('/auth/signup')) {
                        window.location.href = '/auth/login';
                    }
                }
            }
            return Promise.reject(error);
        });
    }
    getToken() {
        if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
        ;
        return localStorage.getItem('access_token');
    }
    clearToken() {
        if ("TURBOPACK compile-time truthy", 1) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
        }
    }
    setToken(token) {
        if ("TURBOPACK compile-time truthy", 1) {
            localStorage.setItem('access_token', token);
            // Force update the axios default headers
            this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        }
    }
    async backendHealthCheck() {
        try {
            const response = await this.client.get('/api/health', {
                timeout: 3000
            });
            if (!response.data || response.data.status !== 'healthy') {
                throw new Error('Backend health check failed');
            }
        } catch (error) {
            throw new Error('Backend is not available. Please ensure it is running on http://localhost:8000');
        }
    }
    // Auth endpoints
    async login(email, password) {
        try {
            const response = await this.client.post('/api/v1/auth/login', {
                email,
                password
            });
            return response.data;
        } catch (error) {
            // Handle network errors
            if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error')) {
                throw new Error('Cannot connect to server. Please ensure the backend is running on http://localhost:8000');
            }
            // Re-throw to let the caller handle it
            throw error;
        }
    }
    async logout() {
        await this.client.post('/api/v1/auth/logout');
        this.clearToken();
    }
    async getCurrentUser() {
        const response = await this.client.get('/api/v1/auth/me');
        return response.data;
    }
    async forgotPassword(email) {
        const response = await this.client.post('/api/v1/auth/forgot-password', {
            email
        });
        return response.data;
    }
    async resetPassword(token, newPassword) {
        const response = await this.client.post('/api/v1/auth/reset-password', {
            token,
            new_password: newPassword
        });
        return response.data;
    }
    async adminChangePassword(userId, newPassword, sendEmail = true) {
        const response = await this.client.post(`/api/v1/users/${userId}/change-password`, {
            new_password: newPassword,
            send_email: sendEmail
        });
        return response.data;
    }
    // User endpoints
    async getUsers(skip = 0, limit = 100) {
        const response = await this.client.get('/api/v1/users/', {
            params: {
                skip,
                limit
            }
        });
        return response.data;
    }
    async createUser(userData) {
        const response = await this.client.post('/api/v1/users/', userData);
        return response.data;
    }
    async updateUser(userId, userData) {
        const response = await this.client.put(`/api/v1/users/${String(userId)}`, userData);
        return response.data;
    }
    async deleteUser(userId) {
        await this.client.delete(`/api/v1/users/${String(userId)}`);
    }
    // Track pending requests to prevent duplicates
    pendingRequests = new Map();
    // Helper method for retry logic with timeout and network error handling
    async retryRequest(requestFn, endpointName, retries = 1, timeout = 20000, requestKey// Optional key for deduplication
    ) {
        // Deduplicate requests if key is provided
        if (requestKey && this.pendingRequests.has(requestKey)) {
            return this.pendingRequests.get(requestKey);
        }
        const makeRequest = async ()=>{
            let lastError;
            for(let attempt = 0; attempt <= retries; attempt++){
                try {
                    const result = await requestFn();
                    // Remove from pending on success
                    if (requestKey) {
                        this.pendingRequests.delete(requestKey);
                    }
                    return result;
                } catch (error) {
                    lastError = error;
                    // Don't retry on 401 (auth errors) or 4xx errors
                    if (error.response?.status >= 400 && error.response?.status < 500) {
                        if (requestKey) {
                            this.pendingRequests.delete(requestKey);
                        }
                        throw error;
                    }
                    // Check for timeout or network errors
                    const isTimeout = error.code === 'ECONNABORTED' || error.message?.includes('timeout') || error.isTimeout;
                    const isNetworkError = error.code === 'ERR_NETWORK' || error.message?.includes('Network Error') || error.isNetworkError;
                    // Don't retry on timeout - fail fast
                    if (isTimeout) {
                        if (requestKey) {
                            this.pendingRequests.delete(requestKey);
                        }
                        const timeoutError = new Error(`Request timeout: The server took too long to respond for ${endpointName}. This may indicate a database connection issue. Please check if PostgreSQL is running and the backend is accessible.`);
                        timeoutError.isTimeout = true;
                        timeoutError.code = 'ECONNABORTED';
                        throw timeoutError;
                    }
                    // Retry only on network errors (connection refused, etc.)
                    if (attempt < retries && isNetworkError) {
                        const delay = 1000 * (attempt + 1); // Linear backoff: 1s, 2s
                        // Only log in development mode to reduce console noise
                        if ("TURBOPACK compile-time truthy", 1) {
                            console.warn(`${endpointName} fetch attempt ${attempt + 1}/${retries + 1} failed, retrying in ${delay}ms...`);
                        }
                        await new Promise((resolve)=>setTimeout(resolve, delay));
                        continue;
                    }
                    // If no more retries, mark error appropriately
                    if (isNetworkError) {
                        if (requestKey) {
                            this.pendingRequests.delete(requestKey);
                        }
                        const networkError = new Error(`Network error: Cannot connect to the backend server for ${endpointName}. Please ensure it is running on http://localhost:8000`);
                        networkError.isNetworkError = true;
                        networkError.code = 'ERR_NETWORK';
                        throw networkError;
                    }
                    // Remove from pending on error
                    if (requestKey) {
                        this.pendingRequests.delete(requestKey);
                    }
                    throw error;
                }
            }
            // If all retries failed, throw the last error with proper marking
            if (requestKey) {
                this.pendingRequests.delete(requestKey);
            }
            throw lastError || new Error(`Failed to fetch ${endpointName}`);
        };
        const requestPromise = makeRequest();
        // Store pending request if key is provided
        if (requestKey) {
            this.pendingRequests.set(requestKey, requestPromise);
        }
        return requestPromise;
    }
    // Connection endpoints
    async getConnections(skip = 0, limit = 100, retries = 1) {
        const requestKey = `connections-${skip}-${limit}`;
        return this.retryRequest(()=>this.client.get('/api/v1/connections/', {
                params: {
                    skip,
                    limit
                },
                timeout: 10000
            }).then((res)=>res.data), 'connections', retries, 10000, requestKey);
    }
    async getConnection(connectionId) {
        const response = await this.client.get(`/api/v1/connections/${connectionId}`);
        return response.data;
    }
    async createConnection(connectionData) {
        console.log('[API Client] createConnection called with:', {
            ...connectionData,
            password: '***'
        });
        const response = await this.client.post('/api/v1/connections/', connectionData);
        console.log('[API Client] createConnection response:', response.data);
        return response.data;
    }
    async updateConnection(connectionId, connectionData) {
        const response = await this.client.put(`/api/v1/connections/${connectionId}`, connectionData);
        return response.data;
    }
    async deleteConnection(connectionId) {
        await this.client.delete(`/api/v1/connections/${connectionId}`);
    }
    async testConnection(connectionId) {
        // Use longer timeout for connection tests (35s to account for 30s PostgreSQL timeout + overhead)
        const response = await this.client.post(`/api/v1/connections/${connectionId}/test`, {}, {
            timeout: 35000
        });
        return response.data;
    }
    async getConnectionTables(connectionId) {
        const response = await this.client.get(`/api/v1/connections/${connectionId}/tables`);
        return response.data;
    }
    async getTableData(connectionId, tableName, schema, limit = 100, retries = 2, isOracleConnection) {
        const params = new URLSearchParams({
            limit: limit.toString()
        });
        // Only append schema if it's a valid non-empty string (not "undefined" string)
        if (schema && schema !== "undefined" && schema.trim() !== "") {
            params.append('schema', schema.trim());
        }
        const url = `/api/v1/connections/${connectionId}/tables/${tableName}/data?${params}`;
        const fullUrl = `${this.client.defaults.baseURL || ''}${url}`;
        // Enhanced logging for debugging
        if ("TURBOPACK compile-time truthy", 1) {
            console.log('[API Client] getTableData request:', {
                connectionId,
                tableName,
                schema,
                limit,
                url,
                fullUrl,
                baseURL: this.client.defaults.baseURL,
                retries,
                isOracleConnection
            });
        }
        // Check backend health first (but don't fail if it's slow - just log)
        try {
            const healthController = new AbortController();
            const healthTimeout = setTimeout(()=>healthController.abort(), 2000); // 2s timeout for health check
            try {
                await fetch(`${this.client.defaults.baseURL || 'http://localhost:8000'}/api/health`, {
                    method: 'GET',
                    signal: healthController.signal
                });
            } finally{
                clearTimeout(healthTimeout);
            }
        } catch (healthError) {
            // Don't throw - just log, as backend might be slow but still working
            if ("TURBOPACK compile-time truthy", 1) {
                console.warn('[API Client] Backend health check failed, but continuing:', healthError.message);
            }
        }
        let lastError = null;
        // Determine if Oracle or SQL Server connection for timeout adjustment
        // Backend timeout is 120s for Oracle/SQL Server, 60s for others
        // Frontend timeout should be slightly longer to allow backend to complete
        const isOracle = isOracleConnection !== undefined ? isOracleConnection : url.includes('oracle') || connectionId.toString().toLowerCase().includes('oracle');
        const isSqlServer = url.includes('sqlserver') || url.includes('sql-server') || connectionId.toString().toLowerCase().includes('sqlserver');
        // Use 130s for Oracle/SQL Server (slightly longer than backend 120s), 70s for others (slightly longer than backend 60s)
        const frontendTimeout = isOracle || isSqlServer ? 130000 : 70000;
        for(let attempt = 0; attempt <= retries; attempt++){
            const controller = new AbortController();
            const timeoutId = setTimeout(()=>{
                controller.abort();
            }, frontendTimeout);
            try {
                const response = await this.client.get(url, {
                    timeout: frontendTimeout,
                    signal: controller.signal
                });
                clearTimeout(timeoutId);
                // Validate response
                if (!response || !response.data) {
                    throw new Error('Backend returned an empty or invalid response');
                }
                // Check if response has expected structure
                if (typeof response.data !== 'object') {
                    throw new Error('Backend returned an invalid response format');
                }
                return response.data;
            } catch (err) {
                clearTimeout(timeoutId);
                lastError = err;
                // Enhanced error logging for debugging
                if ("TURBOPACK compile-time truthy", 1) {
                    console.error(`[API Client] getTableData error (attempt ${attempt + 1}/${retries + 1}):`, {
                        name: err.name,
                        code: err.code,
                        message: err.message,
                        response: err.response ? {
                            status: err.response.status,
                            statusText: err.response.statusText,
                            data: err.response.data
                        } : null,
                        isNetworkError: !err.response,
                        fullUrl
                    });
                }
                // IMPORTANT: Check for HTTP responses FIRST (before timeout/network checks)
                // This ensures 500 errors are properly handled as server errors, not network errors
                // Check for server errors (500+) - don't retry these
                if (err.response && err.response.status >= 500) {
                    // Server error - don't retry, just store and break
                    lastError = err;
                    break;
                }
                // Check for client errors (400-499) - don't retry these
                if (err.response && err.response.status >= 400 && err.response.status < 500) {
                    // Client error - don't retry, just store and break
                    lastError = err;
                    break;
                }
                // Don't retry on abort/timeout - fail fast
                if (err.name === 'AbortError' || err.code === 'ECONNABORTED' || err.message?.includes('aborted')) {
                    if (isOracle) {
                        lastError = new Error('Oracle Connection Timeout: The request to Oracle database timed out.\n\n' + 'This usually means:\n' + '1. Oracle server is not reachable\n' + '2. Oracle listener is not running\n' + '3. Network/firewall is blocking the connection\n' + '4. Service name is incorrect\n\n' + 'Please check:\n' + '- Oracle server is running and accessible\n' + '- Oracle listener is active (run "lsnrctl status" on Oracle server)\n' + '- Network connectivity to Oracle server\n' + '- Service name is correct (should be XE, ORCL, PDB1, etc.)\n' + '- Firewall allows connections on Oracle port');
                        lastError.isTimeout = true;
                        lastError.code = 'ECONNABORTED';
                    } else {
                        lastError = new Error('Request timeout: The database query took too long. Please try again or check your database connection.');
                        lastError.isTimeout = true;
                        lastError.code = 'ECONNABORTED';
                    }
                    break; // Don't retry timeouts
                }
                // Check for empty response or parsing errors - don't retry
                if (err.response && (!err.response.data || typeof err.response.data === 'object' && Object.keys(err.response.data).length === 0)) {
                    lastError = new Error('Server returned an empty response. The backend may have crashed or encountered an error. Please check the backend logs.');
                    lastError.isNetworkError = true;
                    break; // Don't retry empty responses
                }
                // Check for network errors - retry if not last attempt
                // ONLY check for network errors if there's NO response (error.response is null/undefined)
                const isNetworkError = !err.response && (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK' || err.code === 'ERR_INTERNET_DISCONNECTED' || err.message === 'Network Error' || err.message?.includes('Network Error'));
                if (isNetworkError && attempt < retries) {
                    // Wait before retry (exponential backoff)
                    const delay = Math.min(1000 * Math.pow(2, attempt), 5000);
                    console.log(`[API Client] Network error, retrying in ${delay}ms (attempt ${attempt + 1}/${retries + 1})`);
                    await new Promise((resolve)=>setTimeout(resolve, delay));
                    continue; // Retry
                }
                break;
            }
        }
        // Process final error - only if we have one
        if (!lastError) {
            throw new Error('Unexpected error: No error was captured but request failed');
        }
        const error = lastError;
        // Log the full error for debugging - handle different error types
        if ("TURBOPACK compile-time truthy", 1) {
            const errorInfo = {
                errorType: typeof error,
                errorConstructor: error?.constructor?.name,
                isError: error instanceof Error
            };
            // Try to extract all possible error properties
            if (error instanceof Error) {
                errorInfo.message = error.message;
                errorInfo.name = error.name;
                errorInfo.stack = error.stack;
            }
            // Check for axios error properties
            if (error.response) {
                errorInfo.response = {
                    status: error.response.status,
                    statusText: error.response.statusText,
                    data: error.response.data,
                    headers: error.response.headers
                };
            }
            // Check for axios request properties
            if (error.request) {
                errorInfo.request = {
                    method: error.config?.method,
                    url: error.config?.url,
                    timeout: error.config?.timeout
                };
            }
            // Check for custom properties
            errorInfo.code = error.code;
            errorInfo.isTimeout = error.isTimeout;
            errorInfo.isNetworkError = error.isNetworkError;
            errorInfo.config = error.config;
            // If error is a string, include it
            if (typeof error === 'string') {
                errorInfo.stringValue = error;
            }
            // Try JSON.stringify to see the full object
            try {
                errorInfo.jsonString = JSON.stringify(error, Object.getOwnPropertyNames(error));
            } catch (e) {
                errorInfo.jsonError = String(e);
            }
            console.error('[API Client] getTableData error:', errorInfo);
            console.error('[API Client] Raw error object:', error);
        }
        // Extract error message - handle different error types
        let errorMessage = '';
        if (typeof error === 'string') {
            errorMessage = error;
        } else if (error?.message) {
            errorMessage = error.message;
        } else if (error?.response?.data?.detail) {
            errorMessage = error.response.data.detail;
        } else if (error?.response?.data?.message) {
            errorMessage = error.response.data.message;
        } else if (error?.response?.statusText) {
            errorMessage = error.response.statusText;
        } else {
            errorMessage = 'Unknown error occurred';
        }
        // Check for HTTP status codes FIRST (before network/timeout errors)
        // This ensures we properly handle validation errors, server errors, etc.
        // Check for validation errors (422) - these are NOT network errors
        if (error.response?.status === 422) {
            const validationError = error.response?.data?.detail || errorMessage || 'Validation error';
            // Check if it's a list of validation errors (Pydantic format)
            if (Array.isArray(validationError)) {
                const errorDetails = validationError.map((err)=>{
                    if (typeof err === 'object' && err.loc && err.msg) {
                        return `${err.loc.join('.')}: ${err.msg}`;
                    }
                    return String(err);
                }).join('\n');
                throw new Error(`Validation Error: Invalid request parameters.\n\n${errorDetails}\n\nPlease check:\n- Connection ID is valid\n- Table name is correct\n- Schema name is correct (if provided)`);
            }
            throw new Error(`Validation Error: ${validationError}\n\nPlease check:\n- Connection ID is valid\n- Table name is correct\n- Schema name is correct (if provided)`);
        }
        // Check for other client errors (400-499) - but not 422 (already handled above)
        if (error.response?.status >= 400 && error.response?.status < 500 && error.response?.status !== 422) {
            const errorDetail = error.response?.data?.detail || errorMessage || 'Invalid request';
            throw new Error(`Request Error (${error.response.status}): ${errorDetail}`);
        }
        // Check for server errors (500+) - handle these with detailed messages
        if (error.response?.status >= 500) {
            let errorDetail = error.response?.data?.detail || error.response?.data || errorMessage || 'Server error occurred';
            // If errorDetail is a string, use it directly; if it's an object, try to extract message
            if (typeof errorDetail === 'object') {
                errorDetail = errorDetail.message || errorDetail.error || JSON.stringify(errorDetail);
            }
            // Check if this is an Oracle-related error
            const isOracleError = typeof errorDetail === 'string' && (errorDetail.toLowerCase().includes('oracle') || errorDetail.toLowerCase().includes('ora-') || errorDetail.toLowerCase().includes('service name') || errorDetail.toLowerCase().includes('listener'));
            if (isOracleError) {
                throw new Error(`Oracle Database Error:\n\n${errorDetail}\n\n` + `Troubleshooting Steps:\n` + `1. Verify Oracle server is running and accessible\n` + `2. Check Oracle listener: Run 'lsnrctl status' on Oracle server\n` + `3. Test network connectivity: ping the Oracle host and telnet to the Oracle port\n` + `4. Verify service name: Should be XE, ORCL, PDB1, etc. (NOT your username)\n` + `5. Check firewall: Ensure Oracle port (usually 1521) is not blocked\n` + `6. Verify credentials: Username and password are correct\n\n` + `Please check the backend terminal logs for more details.`);
            }
            throw new Error(`Server Error (${error.response.status}): ${errorDetail}\n\nPlease check the backend terminal logs for more details.`);
        }
        // Check for gateway timeout (504)
        if (error.response?.status === 504) {
            throw new Error(`Request timeout: The backend took too long to fetch data from the database. The table "${tableName}" may be very large or the database connection is slow.`);
        }
        // Check for timeout (before network errors)
        if (error.isTimeout || error.code === 'ECONNABORTED' || errorMessage?.includes('timeout') || errorMessage?.includes('Timeout')) {
            // Check if this is likely an Oracle connection issue
            const isOracleIssue = errorMessage?.toLowerCase().includes('oracle') || errorMessage?.toLowerCase().includes('ora-') || tableName?.toLowerCase().includes('oracle');
            if (isOracleIssue) {
                throw new Error(`Oracle Connection Timeout: The request to fetch table data from Oracle timed out.\n\n` + `This usually means:\n` + `1. Oracle database server is not reachable\n` + `2. Oracle listener is not running\n` + `3. Network/firewall is blocking the connection\n` + `4. Service name is incorrect\n\n` + `Please check:\n` + `- Oracle server is running and accessible\n` + `- Oracle listener is active (run 'lsnrctl status' on Oracle server)\n` + `- Network connectivity to Oracle server\n` + `- Service name is correct (should be XE, ORCL, PDB1, etc., NOT your username)\n` + `- Firewall allows connections on Oracle port (usually 1521)\n\n` + `Try reducing the number of records or check the Oracle connection configuration.`);
            }
            throw new Error(`Timeout while fetching table data. The table "${tableName}" may be very large or the database connection is slow. Try reducing the limit.`);
        }
        // Check for empty response (backend may have crashed or returned invalid response)
        if (error.response && (!error.response.data || typeof error.response.data === 'object' && Object.keys(error.response.data).length === 0)) {
            throw new Error('Server returned an empty response. The backend may have encountered an error. Please check the backend logs and try again.');
        }
        // Check for network errors - ONLY if there's NO response (error.response is null/undefined)
        // This means the request never reached the server or the server didn't respond
        // This can happen if: backend crashes, CORS blocks, connection refused, or request times out
        // IMPORTANT: Only treat as network error if there's NO response (error.response is null/undefined)
        const isNetworkError = !error.response && (error.isNetworkError || error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK' || error.code === 'ERR_INTERNET_DISCONNECTED' || error.code === 'ERR_CONNECTION_REFUSED' || error.code === 'ETIMEDOUT' || errorMessage === 'Network Error' || errorMessage?.includes('Network Error') || errorMessage?.includes('Cannot connect to server') || errorMessage?.includes('Failed to load response data') || error.name === 'AxiosError' && errorMessage === 'Network Error' || error.request && !error.response // Request was made but no response received
        );
        if (isNetworkError) {
            // Check if backend is still alive
            let backendAlive = false;
            try {
                const healthController = new AbortController();
                const healthTimeout = setTimeout(()=>healthController.abort(), 3000);
                try {
                    const healthCheck = await fetch('http://localhost:8000/api/health', {
                        method: 'GET',
                        signal: healthController.signal
                    });
                    backendAlive = healthCheck.ok;
                } finally{
                    clearTimeout(healthTimeout);
                }
            } catch (healthErr) {
                backendAlive = false;
            }
            // Provide a helpful error message with troubleshooting steps
            let troubleshootingMsg = `Network Error: The request to fetch table data failed.\n\n`;
            if (!backendAlive) {
                troubleshootingMsg += `⚠️ Backend is not responding. The server may have crashed.\n\n`;
            } else {
                troubleshootingMsg += `⚠️ Backend is running but the request timed out or failed.\n\n`;
            }
            troubleshootingMsg += `Possible causes:\n` + `1. Database connection is hanging (Oracle/SQL Server may be unreachable)\n` + `2. Backend server crashed or is not responding\n` + `3. Request timeout (table may be too large or database is slow)\n` + `4. Network connectivity issue\n\n` + `Please check:\n` + `- Backend is running on http://localhost:8000\n` + `- Check backend terminal for error logs\n` + `- Database servers are accessible and responding\n` + `- Try the "Retry Target" button\n` + `- Reduce the number of records if table is very large`;
            throw new Error(troubleshootingMsg);
        }
        // If we get here and have a response, it's an unhandled status code
        if (error.response) {
            const status = error.response.status;
            const errorDetail = error.response?.data?.detail || errorMessage || `HTTP ${status} error`;
            throw new Error(`Request failed with status ${status}: ${errorDetail}`);
        }
        // Re-throw with a meaningful message
        throw new Error(errorMessage || 'An unexpected error occurred while fetching table data');
    }
    // Pipeline endpoints
    async getPipelines(skip, limit, retries) {
        const skipValue = skip ?? 0;
        const limitValue = limit ?? 100;
        const retriesValue = retries ?? 1;
        const requestKey = `pipelines-${skipValue}-${limitValue}`;
        return this.retryRequest(()=>this.client.get('/api/v1/pipelines/', {
                params: {
                    skip: skipValue,
                    limit: limitValue
                },
                timeout: 10000
            }).then((res)=>res.data), 'pipelines', retriesValue, 10000, requestKey);
    }
    async getPipeline(pipelineId) {
        const response = await this.client.get(`/api/v1/pipelines/${pipelineId}`);
        return response.data;
    }
    async fixOrphanedConnections() {
        const response = await this.client.post('/api/v1/pipelines/fix-orphaned-connections');
        return response.data;
    }
    async createPipeline(pipelineData) {
        try {
            console.log('[API Client] createPipeline called with:', {
                ...pipelineData,
                table_mappings: pipelineData.table_mappings?.length || 0
            });
            const response = await this.client.post('/api/v1/pipelines/', pipelineData);
            console.log('[API Client] createPipeline success:', response.data);
            return response.data;
        } catch (error) {
            // Log comprehensive error information
            const errorInfo = {
                message: error.message || 'Unknown error',
                name: error.name,
                code: error.code,
                isTimeout: error.isTimeout,
                isNetworkError: error.isNetworkError
            };
            // Add response data if available
            if (error.response) {
                errorInfo.status = error.response.status;
                errorInfo.statusText = error.response.statusText;
                errorInfo.data = error.response.data;
                errorInfo.headers = error.response.headers;
            }
            // Add request config if available
            if (error.config) {
                errorInfo.url = error.config.url;
                errorInfo.method = error.config.method;
                errorInfo.data = error.config.data;
            }
            // Log the full error object
            console.error('[API Client] createPipeline error:', errorInfo);
            console.error('[API Client] Full error object:', error);
            // Re-throw with better error message
            if (error.response?.data?.detail) {
                const detailedError = new Error(error.response.data.detail);
                detailedError.response = error.response;
                detailedError.status = error.response.status;
                throw detailedError;
            }
            throw error;
        }
    }
    async updatePipeline(pipelineId, pipelineData) {
        const response = await this.client.put(`/api/v1/pipelines/${String(pipelineId)}`, pipelineData);
        return response.data;
    }
    async deletePipeline(pipelineId) {
        await this.client.delete(`/api/v1/pipelines/${pipelineId}`);
    }
    async exportPipelineDag(pipelineId) {
        const response = await this.client.get(`/api/v1/pipelines/${String(pipelineId)}/export-dag`, {
            responseType: 'blob'
        });
        return response.data;
    }
    // Checkpoint management
    async getPipelineCheckpoints(pipelineId) {
        // LSN metrics router is under /monitoring prefix, but endpoints start with /pipelines
        // Increase timeout as this endpoint may query multiple collections and potentially connect to source DB
        const response = await this.client.get(`/api/v1/monitoring/pipelines/${String(pipelineId)}/checkpoints`, {
            timeout: 20000 // 20 seconds timeout
        });
        return response.data;
    }
    async getPipelineCheckpoint(pipelineId, tableName, schemaName) {
        const params = schemaName ? {
            schema_name: schemaName
        } : {};
        const response = await this.client.get(`/api/v1/pipelines/${String(pipelineId)}/checkpoints/${encodeURIComponent(tableName)}`, {
            params
        });
        return response.data;
    }
    async updatePipelineCheckpoint(pipelineId, tableName, checkpointData, schemaName) {
        const params = schemaName ? {
            schema_name: schemaName
        } : {};
        const response = await this.client.put(`/api/v1/pipelines/${String(pipelineId)}/checkpoints/${encodeURIComponent(tableName)}`, checkpointData, {
            params
        });
        return response.data;
    }
    async resetPipelineCheckpoint(pipelineId, tableName, schemaName) {
        const params = schemaName ? {
            schema_name: schemaName
        } : {};
        const response = await this.client.delete(`/api/v1/pipelines/${String(pipelineId)}/checkpoints/${encodeURIComponent(tableName)}`, {
            params
        });
        return response.data;
    }
    async triggerPipeline(pipelineId, runType = 'full_load') {
        const response = await this.client.post(`/api/v1/pipelines/${String(pipelineId)}/trigger`, {
            run_type: runType
        });
        return response.data;
    }
    async syncPipelineStats(pipelineId) {
        const response = await this.client.post(`/api/v1/pipelines/${String(pipelineId)}/sync-stats`);
        return response.data;
    }
    async getPipelineProgress(pipelineId) {
        // Progress endpoint is optimized to return immediately from memory (no DB queries)
        // Using shorter timeout since endpoint should respond instantly
        const response = await this.client.get(`/api/v1/pipelines/${String(pipelineId)}/progress`, {
            timeout: 3000 // 3 seconds timeout (endpoint should respond in <100ms)
        });
        return response.data;
    }
    async pausePipeline(pipelineId) {
        const response = await this.client.post(`/api/v1/pipelines/${String(pipelineId)}/pause`);
        return response.data;
    }
    async stopPipeline(pipelineId) {
        const response = await this.client.post(`/api/v1/pipelines/${String(pipelineId)}/stop`);
        return response.data;
    }
    async getPipelineRuns(pipelineId, skip = 0, limit = 100) {
        const response = await this.client.get(`/api/v1/pipelines/${pipelineId}/runs`, {
            params: {
                skip,
                limit
            }
        });
        return response.data;
    }
    async getPipelineStatus(pipelineId) {
        const response = await this.client.get(`/api/v1/pipelines/${pipelineId}/status`);
        return response.data;
    }
    // Monitoring endpoints
    async getReplicationEvents(pipelineId, skip = 0, limit = 100, todayOnly = false, startDate, endDate, tableName, retries = 1) {
        const requestKey = `events-${pipelineId || 'all'}-${skip}-${limit}-${todayOnly}-${startDate || ''}-${endDate || ''}-${tableName || ''}`;
        // Convert to string for UUIDs, or use as-is for numbers
        const pipelineIdParam = pipelineId ? String(pipelineId) : undefined;
        // Convert Date objects to ISO strings if needed
        const startDateParam = startDate instanceof Date ? startDate.toISOString() : startDate;
        const endDateParam = endDate instanceof Date ? endDate.toISOString() : endDate;
        return this.retryRequest(()=>this.client.get('/api/v1/monitoring/events', {
                params: {
                    pipeline_id: pipelineIdParam,
                    table_name: tableName,
                    skip,
                    limit,
                    today_only: todayOnly,
                    start_date: startDateParam,
                    end_date: endDateParam
                },
                timeout: 10000
            }).then((res)=>res.data), 'replication events', retries, 10000, requestKey);
    }
    async getMonitoringMetrics(pipelineId, startTime, endTime, retries = 1) {
        // Convert to string to handle both numeric IDs and UUID strings
        const pipelineIdStr = String(pipelineId);
        // Don't send if it's NaN
        if (pipelineIdStr === 'NaN' || pipelineIdStr === 'undefined' || !pipelineIdStr) {
            throw new Error('Invalid pipeline ID');
        }
        // Convert Date objects to ISO strings if necessary
        const formattedStartTime = startTime instanceof Date ? startTime.toISOString() : startTime;
        const formattedEndTime = endTime instanceof Date ? endTime.toISOString() : endTime;
        const requestKey = `metrics-${pipelineIdStr}-${formattedStartTime || ''}-${formattedEndTime || ''}`;
        return this.retryRequest(()=>this.client.get('/api/v1/monitoring/metrics', {
                params: {
                    pipeline_id: pipelineIdStr,
                    start_time: formattedStartTime,
                    end_time: formattedEndTime
                },
                timeout: 10000
            }).then((res)=>res.data), 'monitoring metrics', retries, 10000, requestKey);
    }
    async retryFailedEvent(eventId) {
        const response = await this.client.post(`/api/v1/monitoring/events/${eventId}/retry`);
        return response.data;
    }
    async createReplicationEvent(eventData) {
        const response = await this.client.post('/api/v1/monitoring/events', eventData);
        return response.data;
    }
    // LSN Latency methods
    async getLsnLatency(pipelineId, tableName, schemaName) {
        const params = {};
        if (tableName) params.table_name = tableName;
        if (schemaName) params.schema_name = schemaName;
        // LSN metrics router is under /monitoring prefix, but endpoints start with /pipelines
        const response = await this.client.get(`/api/v1/monitoring/pipelines/${String(pipelineId)}/lsn-latency`, {
            params
        });
        return response.data;
    }
    async getLsnLatencyTrend(pipelineId, tableName, hours = 24) {
        const params = {
            hours
        };
        if (tableName) params.table_name = tableName;
        const response = await this.client.get(`/api/v1/monitoring/pipelines/${String(pipelineId)}/lsn-latency-trend`, {
            params
        });
        return response.data;
    }
    async getLsnLatencyMetrics(pipelineId, startTime, endTime, limit = 100) {
        const params = {
            limit
        };
        if (startTime) params.start_time = startTime;
        if (endTime) params.end_time = endTime;
        const response = await this.client.get(`/api/v1/monitoring/lsn-latency`, {
            params: {
                pipeline_id: pipelineId,
                ...params
            }
        });
        return response.data;
    }
}
const apiClient = new ApiClient();
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/store/slices/authSlice.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
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
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/@reduxjs/toolkit/dist/redux-toolkit.modern.mjs [app-client] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api/client.ts [app-client] (ecmascript)");
;
;
// Helper to safely get from localStorage
const getInitialToken = ()=>{
    if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
    ;
    try {
        return localStorage.getItem('access_token');
    } catch  {
        return null;
    }
};
// Helper to safely get user from localStorage
const getInitialUser = ()=>{
    if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
    ;
    try {
        const userStr = localStorage.getItem('user');
        if (userStr) {
            return JSON.parse(userStr);
        }
    } catch  {
        return null;
    }
    return null;
};
const initialState = {
    user: getInitialUser(),
    token: getInitialToken(),
    isAuthenticated: !!getInitialToken(),
    isLoading: false,
    error: null
};
const login = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('auth/login', async ({ email, password }, { rejectWithValue })=>{
    try {
        // Step 1: Login and get token
        const data = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].login(email, password);
        if (!data.access_token) {
            return rejectWithValue('No access token received from server');
        }
        // Step 2: Set token in API client and localStorage
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].setToken(data.access_token);
        // Step 3: Wait a bit to ensure token is set, then get user info
        // Small delay to ensure localStorage is updated
        await new Promise((resolve)=>setTimeout(resolve, 100));
        // Step 4: Get current user info
        try {
            const user = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].getCurrentUser();
            return {
                token: data.access_token,
                user
            };
        } catch (userError) {
            // If getting user fails, still return the token
            // User info can be fetched later
            console.warn('Failed to fetch user info after login:', userError);
            return {
                token: data.access_token,
                user: {
                    email,
                    id: 0,
                    full_name: email,
                    is_active: true,
                    is_superuser: false,
                    roles: []
                }
            };
        }
    } catch (error) {
        const errorMessage = error.response?.data?.detail || error.message || 'Login failed';
        return rejectWithValue(errorMessage);
    }
});
const logout = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('auth/logout', async ()=>{
    await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].logout();
});
const getCurrentUser = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('auth/getCurrentUser', async (_, { rejectWithValue })=>{
    try {
        const user = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].getCurrentUser();
        console.log('[Auth] getCurrentUser response:', {
            email: user?.email,
            is_superuser: user?.is_superuser,
            full_user: user
        });
        // Validate that is_superuser is a boolean
        if (user && typeof user.is_superuser !== 'boolean') {
            console.warn('[Auth] is_superuser is not a boolean, defaulting to false. User data:', user);
            user.is_superuser = false;
        }
        if ("TURBOPACK compile-time truthy", 1) {
            localStorage.setItem('user', JSON.stringify(user));
        }
        return user;
    } catch (error) {
        console.error('[Auth] Failed to fetch current user:', error);
        if ("TURBOPACK compile-time truthy", 1) {
            localStorage.removeItem('user');
            localStorage.removeItem('access_token');
        }
        return rejectWithValue(error.response?.data?.detail || 'Failed to fetch user info');
    }
});
const createUser = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('auth/createUser', async (userData, { rejectWithValue })=>{
    try {
        const user = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].createUser(userData);
        return user;
    } catch (error) {
        return rejectWithValue(error.response?.data?.detail || 'Failed to create account');
    }
});
const authSlice = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createSlice"])({
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
            state.user = action.payload.user;
            state.isAuthenticated = true;
            if ("TURBOPACK compile-time truthy", 1) {
                localStorage.setItem('user', JSON.stringify(action.payload.user));
            }
        }).addCase(login.rejected, (state, action)=>{
            state.isLoading = false;
            state.error = action.payload;
        })// Logout
        .addCase(logout.fulfilled, (state)=>{
            state.user = null;
            state.token = null;
            state.isAuthenticated = false;
            if ("TURBOPACK compile-time truthy", 1) {
                localStorage.removeItem('user');
            }
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
            if (("TURBOPACK compile-time value", "object") !== 'undefined' && userData) {
                localStorage.setItem('user', JSON.stringify(state.user));
            }
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
                if ("TURBOPACK compile-time truthy", 1) {
                    localStorage.removeItem('user');
                    localStorage.removeItem('access_token');
                }
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
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/ui/dropdown-menu.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
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
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@radix-ui/react-dropdown-menu/dist/index.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/utils.ts [app-client] (ecmascript)");
"use client";
;
;
;
;
const DropdownMenu = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Root"];
const DropdownMenuTrigger = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Trigger"];
const DropdownMenuGroup = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Group"];
const DropdownMenuPortal = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Portal"];
const DropdownMenuSub = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Sub"];
const DropdownMenuRadioGroup = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["RadioGroup"];
const DropdownMenuSubTrigger = /*#__PURE__*/ __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["forwardRef"](_c = ({ className, inset, children, ...props }, ref)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["SubTrigger"], {
        ref: ref,
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["cn"])("flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none focus:bg-surface-hover data-[state=open]:bg-surface-hover", inset && "pl-8", className),
        ...props,
        children: [
            children,
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
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
_c1 = DropdownMenuSubTrigger;
DropdownMenuSubTrigger.displayName = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["SubTrigger"].displayName;
const DropdownMenuSubContent = /*#__PURE__*/ __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["forwardRef"](_c2 = ({ className, ...props }, ref)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["SubContent"], {
        ref: ref,
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["cn"])("z-50 min-w-[8rem] overflow-hidden rounded-md border border-border bg-surface p-1 text-foreground shadow-lg data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2", className),
        ...props
    }, void 0, false, {
        fileName: "[project]/components/ui/dropdown-menu.tsx",
        lineNumber: 45,
        columnNumber: 3
    }, ("TURBOPACK compile-time value", void 0)));
_c3 = DropdownMenuSubContent;
DropdownMenuSubContent.displayName = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["SubContent"].displayName;
const DropdownMenuContent = /*#__PURE__*/ __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["forwardRef"](_c4 = ({ className, sideOffset = 4, ...props }, ref)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Portal"], {
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Content"], {
            ref: ref,
            sideOffset: sideOffset,
            className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["cn"])("z-50 min-w-[8rem] overflow-hidden rounded-md border border-border bg-surface p-1 text-foreground shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2", className),
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
_c5 = DropdownMenuContent;
DropdownMenuContent.displayName = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Content"].displayName;
const DropdownMenuItem = /*#__PURE__*/ __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["forwardRef"](_c6 = ({ className, inset, ...props }, ref)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Item"], {
        ref: ref,
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["cn"])("relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors focus:bg-surface-hover focus:text-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50", inset && "pl-8", className),
        ...props
    }, void 0, false, {
        fileName: "[project]/components/ui/dropdown-menu.tsx",
        lineNumber: 80,
        columnNumber: 3
    }, ("TURBOPACK compile-time value", void 0)));
_c7 = DropdownMenuItem;
DropdownMenuItem.displayName = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Item"].displayName;
const DropdownMenuCheckboxItem = /*#__PURE__*/ __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["forwardRef"](_c8 = ({ className, children, checked, ...props }, ref)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CheckboxItem"], {
        ref: ref,
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["cn"])("relative flex cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none transition-colors focus:bg-surface-hover focus:text-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50", className),
        checked: checked,
        ...props,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                className: "absolute left-2 flex h-3.5 w-3.5 items-center justify-center",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ItemIndicator"], {
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
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
_c9 = DropdownMenuCheckboxItem;
DropdownMenuCheckboxItem.displayName = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CheckboxItem"].displayName;
const DropdownMenuRadioItem = /*#__PURE__*/ __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["forwardRef"](_c10 = ({ className, children, ...props }, ref)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["RadioItem"], {
        ref: ref,
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["cn"])("relative flex cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none transition-colors focus:bg-surface-hover focus:text-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50", className),
        ...props,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                className: "absolute left-2 flex h-3.5 w-3.5 items-center justify-center",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ItemIndicator"], {
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
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
_c11 = DropdownMenuRadioItem;
DropdownMenuRadioItem.displayName = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["RadioItem"].displayName;
const DropdownMenuLabel = /*#__PURE__*/ __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["forwardRef"](_c12 = ({ className, inset, ...props }, ref)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Label"], {
        ref: ref,
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["cn"])("px-2 py-1.5 text-sm font-semibold", inset && "pl-8", className),
        ...props
    }, void 0, false, {
        fileName: "[project]/components/ui/dropdown-menu.tsx",
        lineNumber: 143,
        columnNumber: 3
    }, ("TURBOPACK compile-time value", void 0)));
_c13 = DropdownMenuLabel;
DropdownMenuLabel.displayName = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Label"].displayName;
const DropdownMenuSeparator = /*#__PURE__*/ __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["forwardRef"](_c14 = ({ className, ...props }, ref)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Separator"], {
        ref: ref,
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["cn"])("-mx-1 my-1 h-px bg-border", className),
        ...props
    }, void 0, false, {
        fileName: "[project]/components/ui/dropdown-menu.tsx",
        lineNumber: 155,
        columnNumber: 3
    }, ("TURBOPACK compile-time value", void 0)));
_c15 = DropdownMenuSeparator;
DropdownMenuSeparator.displayName = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$dropdown$2d$menu$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Separator"].displayName;
const DropdownMenuShortcut = ({ className, ...props })=>{
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["cn"])("ml-auto text-xs tracking-widest opacity-60", className),
        ...props
    }, void 0, false, {
        fileName: "[project]/components/ui/dropdown-menu.tsx",
        lineNumber: 164,
        columnNumber: 10
    }, ("TURBOPACK compile-time value", void 0));
};
_c16 = DropdownMenuShortcut;
DropdownMenuShortcut.displayName = "DropdownMenuShortcut";
;
var _c, _c1, _c2, _c3, _c4, _c5, _c6, _c7, _c8, _c9, _c10, _c11, _c12, _c13, _c14, _c15, _c16;
__turbopack_context__.k.register(_c, "DropdownMenuSubTrigger$React.forwardRef");
__turbopack_context__.k.register(_c1, "DropdownMenuSubTrigger");
__turbopack_context__.k.register(_c2, "DropdownMenuSubContent$React.forwardRef");
__turbopack_context__.k.register(_c3, "DropdownMenuSubContent");
__turbopack_context__.k.register(_c4, "DropdownMenuContent$React.forwardRef");
__turbopack_context__.k.register(_c5, "DropdownMenuContent");
__turbopack_context__.k.register(_c6, "DropdownMenuItem$React.forwardRef");
__turbopack_context__.k.register(_c7, "DropdownMenuItem");
__turbopack_context__.k.register(_c8, "DropdownMenuCheckboxItem$React.forwardRef");
__turbopack_context__.k.register(_c9, "DropdownMenuCheckboxItem");
__turbopack_context__.k.register(_c10, "DropdownMenuRadioItem$React.forwardRef");
__turbopack_context__.k.register(_c11, "DropdownMenuRadioItem");
__turbopack_context__.k.register(_c12, "DropdownMenuLabel$React.forwardRef");
__turbopack_context__.k.register(_c13, "DropdownMenuLabel");
__turbopack_context__.k.register(_c14, "DropdownMenuSeparator$React.forwardRef");
__turbopack_context__.k.register(_c15, "DropdownMenuSeparator");
__turbopack_context__.k.register(_c16, "DropdownMenuShortcut");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/layout/top-nav.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "TopNav",
    ()=>TopNav
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$user$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__User$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/user.js [app-client] (ecmascript) <export default as User>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$bell$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Bell$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/bell.js [app-client] (ecmascript) <export default as Bell>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/settings.js [app-client] (ecmascript) <export default as Settings>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$moon$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Moon$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/moon.js [app-client] (ecmascript) <export default as Moon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sun$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sun$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/sun.js [app-client] (ecmascript) <export default as Sun>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$out$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__LogOut$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/log-out.js [app-client] (ecmascript) <export default as LogOut>");
var __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$theme$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/contexts/theme-context.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/hooks.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$authSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/authSlice.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/ui/dropdown-menu.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
;
;
;
function TopNav() {
    _s();
    const { theme, toggleTheme } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$theme$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useTheme"])();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"])();
    const dispatch = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppDispatch"])();
    const { user } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppSelector"])({
        "TopNav.useAppSelector": (state)=>state.auth
    }["TopNav.useAppSelector"]);
    const { unreadCount } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppSelector"])({
        "TopNav.useAppSelector": (state)=>state.alerts
    }["TopNav.useAppSelector"]);
    const [mounted, setMounted] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "TopNav.useEffect": ()=>{
            setMounted(true);
        }
    }["TopNav.useEffect"], []);
    const handleLogout = async ()=>{
        try {
            await dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$authSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["logout"])());
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
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "h-16 border-b border-border bg-sidebar flex items-center justify-between px-6",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                        className: "text-xl font-semibold text-foreground",
                        children: "Change Data Capture Platform"
                    }, void 0, false, {
                        fileName: "[project]/components/layout/top-nav.tsx",
                        lineNumber: 48,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
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
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex items-center gap-4",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        onClick: ()=>router.push("/errors"),
                        className: "relative p-2 hover:bg-surface-hover rounded-lg transition-colors hover:text-primary",
                        "aria-label": "Notifications",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$bell$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Bell$3e$__["Bell"], {
                                className: "w-5 h-5 text-foreground-muted hover:text-primary transition-colors"
                            }, void 0, false, {
                                fileName: "[project]/components/layout/top-nav.tsx",
                                lineNumber: 58,
                                columnNumber: 11
                            }, this),
                            mounted && unreadCount > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
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
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        className: "p-2 hover:bg-surface-hover rounded-lg transition-colors hover:text-primary",
                        "aria-label": "Settings",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__["Settings"], {
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
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        onClick: toggleTheme,
                        className: "p-2 hover:bg-surface-hover rounded-lg transition-colors hover:text-primary",
                        "aria-label": "Toggle theme",
                        suppressHydrationWarning: true,
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sun$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sun$3e$__["Sun"], {
                                className: `w-5 h-5 text-foreground-muted ${mounted && theme === "dark" ? "block" : "hidden"}`
                            }, void 0, false, {
                                fileName: "[project]/components/layout/top-nav.tsx",
                                lineNumber: 74,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$moon$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Moon$3e$__["Moon"], {
                                className: `w-5 h-5 text-foreground-muted ${mounted && theme === "light" ? "block" : "hidden"}`
                            }, void 0, false, {
                                fileName: "[project]/components/layout/top-nav.tsx",
                                lineNumber: 75,
                                columnNumber: 11
                            }, this),
                            !mounted && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$moon$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Moon$3e$__["Moon"], {
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
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        suppressHydrationWarning: true,
                        children: mounted ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["DropdownMenu"], {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["DropdownMenuTrigger"], {
                                    asChild: true,
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        className: "p-2 hover:bg-surface-hover rounded-lg transition-colors hover:text-primary",
                                        "aria-label": "User menu",
                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$user$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__User$3e$__["User"], {
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
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["DropdownMenuContent"], {
                                    align: "end",
                                    className: "bg-surface border-border",
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["DropdownMenuLabel"], {
                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                className: "flex flex-col space-y-1",
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                        className: "text-sm font-medium text-foreground",
                                                        children: userName
                                                    }, void 0, false, {
                                                        fileName: "[project]/components/layout/top-nav.tsx",
                                                        lineNumber: 91,
                                                        columnNumber: 21
                                                    }, this),
                                                    userEmail && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
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
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["DropdownMenuSeparator"], {}, void 0, false, {
                                            fileName: "[project]/components/layout/top-nav.tsx",
                                            lineNumber: 95,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["DropdownMenuItem"], {
                                            onClick: ()=>router.push("/settings"),
                                            className: "cursor-pointer",
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__["Settings"], {
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
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["DropdownMenuSeparator"], {}, void 0, false, {
                                            fileName: "[project]/components/layout/top-nav.tsx",
                                            lineNumber: 100,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$dropdown$2d$menu$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["DropdownMenuItem"], {
                                            onClick: handleLogout,
                                            className: "cursor-pointer text-error focus:text-error",
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$out$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__LogOut$3e$__["LogOut"], {
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
                        }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            className: "p-2 hover:bg-surface-hover rounded-lg transition-colors hover:text-primary",
                            "aria-label": "User menu",
                            disabled: true,
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$user$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__User$3e$__["User"], {
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
_s(TopNav, "hocZX7YsXYlurkESbMMcqopamJA=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$theme$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useTheme"],
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppDispatch"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppSelector"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppSelector"]
    ];
});
_c = TopNav;
var _c;
__turbopack_context__.k.register(_c, "TopNav");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/store/slices/alertsSlice.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
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
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/@reduxjs/toolkit/dist/redux-toolkit.modern.mjs [app-client] (ecmascript) <locals>");
;
const initialState = {
    alerts: [],
    unreadCount: 0,
    lastNotificationTime: null
};
const alertsSlice = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createSlice"])({
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
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/alerts/alert-sync.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Component to sync errors from connections, pipelines, and events to alerts
 */ __turbopack_context__.s([
    "AlertSync",
    ()=>AlertSync
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/hooks.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/alertsSlice.ts [app-client] (ecmascript)");
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
function AlertSync() {
    _s();
    const dispatch = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppDispatch"])();
    const { connections, error: connectionError } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppSelector"])({
        "AlertSync.useAppSelector": (state)=>state.connections
    }["AlertSync.useAppSelector"]);
    const { pipelines, error: pipelineError } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppSelector"])({
        "AlertSync.useAppSelector": (state)=>state.pipelines
    }["AlertSync.useAppSelector"]);
    const { events } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppSelector"])({
        "AlertSync.useAppSelector": (state)=>state.monitoring
    }["AlertSync.useAppSelector"]);
    // Sync connection errors
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "AlertSync.useEffect": ()=>{
            if (connectionError) {
                dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["addAlert"])({
                    id: `conn_error_${Date.now()}`,
                    type: 'error',
                    source: 'connection',
                    message: connectionError,
                    timestamp: new Date().toISOString(),
                    status: 'unresolved',
                    severity: 'high'
                }));
            }
        }
    }["AlertSync.useEffect"], [
        connectionError,
        dispatch
    ]);
    // Sync pipeline errors
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "AlertSync.useEffect": ()=>{
            if (pipelineError) {
                dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["addAlert"])({
                    id: `pipeline_error_${Date.now()}`,
                    type: 'error',
                    source: 'pipeline',
                    message: pipelineError,
                    timestamp: new Date().toISOString(),
                    status: 'unresolved',
                    severity: 'high'
                }));
            }
        }
    }["AlertSync.useEffect"], [
        pipelineError,
        dispatch
    ]);
    // Sync connection test failures
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "AlertSync.useEffect": ()=>{
            const connectionsArray = Array.isArray(connections) ? connections : [];
            connectionsArray.forEach({
                "AlertSync.useEffect": (conn)=>{
                    if (conn.last_test_status === 'failed' || !conn.is_active && conn.last_tested_at) {
                        dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["addAlert"])({
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
                }
            }["AlertSync.useEffect"]);
        }
    }["AlertSync.useEffect"], [
        connections,
        dispatch
    ]);
    // Sync pipeline errors
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "AlertSync.useEffect": ()=>{
            const pipelinesArray = Array.isArray(pipelines) ? pipelines : [];
            pipelinesArray.forEach({
                "AlertSync.useEffect": (pipeline)=>{
                    if (pipeline.status === 'error') {
                        dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["addAlert"])({
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
                }
            }["AlertSync.useEffect"]);
        }
    }["AlertSync.useEffect"], [
        pipelines,
        dispatch
    ]);
    // Sync replication event errors
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "AlertSync.useEffect": ()=>{
            const eventsArray = Array.isArray(events) ? events : [];
            const failedEvents = eventsArray.filter({
                "AlertSync.useEffect.failedEvents": (e)=>e.status === 'failed' || e.status === 'error'
            }["AlertSync.useEffect.failedEvents"]).slice(0, 100) // Limit to recent 100 failed events
            ;
            if (failedEvents.length > 0) {
                const alerts = failedEvents.map({
                    "AlertSync.useEffect.alerts": (event)=>({
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
                        })
                }["AlertSync.useEffect.alerts"]);
                dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["addAlerts"])(alerts));
            }
        }
    }["AlertSync.useEffect"], [
        events,
        dispatch
    ]);
    return null // This is a sync component, no UI
    ;
}
_s(AlertSync, "+NW7B4ji+2ZIJ1KvkRxGmG+bCpo=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppDispatch"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppSelector"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppSelector"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppSelector"]
    ];
});
_c = AlertSync;
var _c;
__turbopack_context__.k.register(_c, "AlertSync");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/ui/button.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "Button",
    ()=>Button,
    "buttonVariants",
    ()=>buttonVariants
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$slot$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@radix-ui/react-slot/dist/index.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$class$2d$variance$2d$authority$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/class-variance-authority/dist/index.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/utils.ts [app-client] (ecmascript)");
;
;
;
;
const buttonVariants = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$class$2d$variance$2d$authority$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["cva"])("inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive", {
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
    const Comp = asChild ? __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$radix$2d$ui$2f$react$2d$slot$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Slot"] : 'button';
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(Comp, {
        "data-slot": "button",
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["cn"])(buttonVariants({
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
_c = Button;
;
var _c;
__turbopack_context__.k.register(_c, "Button");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/alerts/top-alert-bar.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Top alert bar component to show critical alerts at the top of the page
 */ __turbopack_context__.s([
    "TopAlertBar",
    ()=>TopAlertBar
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/hooks.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/alertsSlice.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/x.js [app-client] (ecmascript) <export default as X>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__AlertTriangle$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/triangle-alert.js [app-client] (ecmascript) <export default as AlertTriangle>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$circle$2d$alert$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__AlertCircle$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/circle-alert.js [app-client] (ecmascript) <export default as AlertCircle>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$info$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Info$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/info.js [app-client] (ecmascript) <export default as Info>");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/ui/button.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$date$2d$fns$2f$formatDistanceToNow$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/date-fns/formatDistanceToNow.js [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
;
;
function TopAlertBar() {
    _s();
    const dispatch = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppDispatch"])();
    const { alerts, unreadCount } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppSelector"])({
        "TopAlertBar.useAppSelector": (state)=>state.alerts
    }["TopAlertBar.useAppSelector"]);
    const [dismissedAlerts, setDismissedAlerts] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(new Set());
    // Get critical/unresolved alerts - memoized to prevent unnecessary recalculations
    const criticalAlerts = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useMemo"])({
        "TopAlertBar.useMemo[criticalAlerts]": ()=>{
            return alerts.filter({
                "TopAlertBar.useMemo[criticalAlerts]": (a)=>a.status === 'unresolved' && (a.severity === 'critical' || a.severity === 'high') && !dismissedAlerts.has(a.id)
            }["TopAlertBar.useMemo[criticalAlerts]"]).slice(0, 3) // Show max 3 alerts
            ;
        }
    }["TopAlertBar.useMemo[criticalAlerts]"], [
        alerts,
        dismissedAlerts
    ]);
    // Request notification permission
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "TopAlertBar.useEffect": ()=>{
            if (("TURBOPACK compile-time value", "object") !== 'undefined' && 'Notification' in window && Notification.permission === 'default') {
                Notification.requestPermission();
            }
        }
    }["TopAlertBar.useEffect"], []);
    // Show browser notifications for new critical alerts
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "TopAlertBar.useEffect": ()=>{
            if (criticalAlerts.length > 0 && ("TURBOPACK compile-time value", "object") !== 'undefined' && 'Notification' in window) {
                const latestAlert = criticalAlerts[0];
                if (Notification.permission === 'granted' && !dismissedAlerts.has(latestAlert.id)) {
                    new Notification('Critical Alert', {
                        body: `${latestAlert.sourceName || latestAlert.source}: ${latestAlert.message}`,
                        icon: '/icon-dark-32x32.png',
                        tag: latestAlert.id
                    });
                }
            }
        }
    }["TopAlertBar.useEffect"], [
        criticalAlerts,
        dismissedAlerts
    ]);
    // Memoize handlers to prevent infinite loops
    const handleAcknowledge = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "TopAlertBar.useCallback[handleAcknowledge]": (alertId)=>{
            dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["updateAlertStatus"])({
                id: alertId,
                status: 'acknowledged'
            }));
            setDismissedAlerts({
                "TopAlertBar.useCallback[handleAcknowledge]": (prev)=>{
                    const newSet = new Set(prev);
                    newSet.add(alertId);
                    return newSet;
                }
            }["TopAlertBar.useCallback[handleAcknowledge]"]);
        }
    }["TopAlertBar.useCallback[handleAcknowledge]"], [
        dispatch
    ]);
    const handleDismiss = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "TopAlertBar.useCallback[handleDismiss]": (alertId)=>{
            setDismissedAlerts({
                "TopAlertBar.useCallback[handleDismiss]": (prev)=>{
                    const newSet = new Set(prev);
                    newSet.add(alertId);
                    return newSet;
                }
            }["TopAlertBar.useCallback[handleDismiss]"]);
        }
    }["TopAlertBar.useCallback[handleDismiss]"], []);
    if (criticalAlerts.length === 0) {
        return null;
    }
    const getAlertIcon = (type, severity)=>{
        if (severity === 'critical') {
            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$circle$2d$alert$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__AlertCircle$3e$__["AlertCircle"], {
                className: "w-5 h-5 text-destructive"
            }, void 0, false, {
                fileName: "[project]/components/alerts/top-alert-bar.tsx",
                lineNumber: 74,
                columnNumber: 14
            }, this);
        }
        if (type === 'error' || severity === 'high') {
            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__AlertTriangle$3e$__["AlertTriangle"], {
                className: "w-5 h-5 text-error"
            }, void 0, false, {
                fileName: "[project]/components/alerts/top-alert-bar.tsx",
                lineNumber: 77,
                columnNumber: 14
            }, this);
        }
        if (type === 'warning') {
            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__AlertTriangle$3e$__["AlertTriangle"], {
                className: "w-5 h-5 text-warning"
            }, void 0, false, {
                fileName: "[project]/components/alerts/top-alert-bar.tsx",
                lineNumber: 80,
                columnNumber: 14
            }, this);
        }
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$info$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Info$3e$__["Info"], {
            className: "w-5 h-5 text-info"
        }, void 0, false, {
            fileName: "[project]/components/alerts/top-alert-bar.tsx",
            lineNumber: 82,
            columnNumber: 12
        }, this);
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "border-b border-border bg-surface",
        children: [
            criticalAlerts.map((alert)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: `px-6 py-3 flex items-center gap-4 ${alert.severity === 'critical' ? 'bg-destructive/10 border-l-4 border-destructive' : alert.severity === 'high' ? 'bg-error/10 border-l-4 border-error' : 'bg-warning/10 border-l-4 border-warning'}`,
                    children: [
                        getAlertIcon(alert.type, alert.severity),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "flex-1",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
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
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                    className: "text-xs text-foreground-muted mt-0.5",
                                    children: (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$date$2d$fns$2f$formatDistanceToNow$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["formatDistanceToNow"])(new Date(alert.timestamp), {
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
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "flex items-center gap-2",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Button"], {
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
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Button"], {
                                    size: "sm",
                                    variant: "ghost",
                                    onClick: (e)=>{
                                        e.preventDefault();
                                        e.stopPropagation();
                                        handleDismiss(alert.id);
                                    },
                                    className: "text-xs h-7 px-2",
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
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
            unreadCount > criticalAlerts.length && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "px-6 py-2 bg-surface-hover text-center",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Button"], {
                    variant: "ghost",
                    size: "sm",
                    onClick: ()=>dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["markAllAsRead"])()),
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
_s(TopAlertBar, "KW26L7ycsy580fY1eaK1o9xo1nw=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppDispatch"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$hooks$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppSelector"]
    ];
});
_c = TopAlertBar;
var _c;
__turbopack_context__.k.register(_c, "TopAlertBar");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/layout/root-layout-wrapper.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "RootLayoutWrapper",
    ()=>RootLayoutWrapper
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$layout$2f$sidebar$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/layout/sidebar.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$layout$2f$top$2d$nav$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/layout/top-nav.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$theme$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/contexts/theme-context.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$sidebar$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/contexts/sidebar-context.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$alerts$2f$alert$2d$sync$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/alerts/alert-sync.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$alerts$2f$top$2d$alert$2d$bar$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/alerts/top-alert-bar.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
;
;
;
function RootLayoutWrapper({ children }) {
    _s();
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["usePathname"])();
    const isAuthPage = pathname?.startsWith("/auth");
    // Auth pages (login, signup) should not have dashboard layout
    if (isAuthPage) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$theme$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ThemeProvider"], {
            children: children
        }, void 0, false, {
            fileName: "[project]/components/layout/root-layout-wrapper.tsx",
            lineNumber: 19,
            columnNumber: 7
        }, this);
    }
    // Dashboard and other pages get the full layout with sidebar and top nav
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$theme$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ThemeProvider"], {
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$sidebar$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["SidebarProvider"], {
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex h-screen bg-sidebar",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$layout$2f$sidebar$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Sidebar"], {}, void 0, false, {
                        fileName: "[project]/components/layout/root-layout-wrapper.tsx",
                        lineNumber: 30,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex-1 flex flex-col overflow-hidden bg-sidebar",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$alerts$2f$alert$2d$sync$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["AlertSync"], {}, void 0, false, {
                                fileName: "[project]/components/layout/root-layout-wrapper.tsx",
                                lineNumber: 34,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$layout$2f$top$2d$nav$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["TopNav"], {}, void 0, false, {
                                fileName: "[project]/components/layout/root-layout-wrapper.tsx",
                                lineNumber: 35,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$alerts$2f$top$2d$alert$2d$bar$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["TopAlertBar"], {}, void 0, false, {
                                fileName: "[project]/components/layout/root-layout-wrapper.tsx",
                                lineNumber: 36,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
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
_s(RootLayoutWrapper, "xbyQPtUVMO7MNj7WjJlpdWqRcTo=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["usePathname"]
    ];
});
_c = RootLayoutWrapper;
var _c;
__turbopack_context__.k.register(_c, "RootLayoutWrapper");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/store/slices/connectionSlice.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
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
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/@reduxjs/toolkit/dist/redux-toolkit.modern.mjs [app-client] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api/client.ts [app-client] (ecmascript)");
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
const fetchConnections = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('connections/fetchAll', async (_, { rejectWithValue })=>{
    try {
        return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].getConnections();
    } catch (error) {
        // Provide more helpful error messages for timeouts
        if (error.isTimeout) {
            return rejectWithValue('Request timeout: The server took too long to respond. This may indicate a database connection issue. Please check if MongoDB is running.');
        }
        if (error.isNetworkError) {
            return rejectWithValue('Network error: Cannot connect to the backend server. Please ensure it is running on http://localhost:8000');
        }
        return rejectWithValue(error.message || 'Failed to fetch connections');
    }
});
const fetchConnection = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('connections/fetchOne', async (id)=>{
    return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].getConnection(id);
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
const createConnection = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('connections/create', async (connectionData, { rejectWithValue })=>{
    try {
        return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].createConnection(connectionData);
    } catch (error) {
        return rejectWithValue(extractErrorMessage(error));
    }
});
const updateConnection = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('connections/update', async ({ id, data }, { rejectWithValue })=>{
    try {
        return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].updateConnection(id, data);
    } catch (error) {
        return rejectWithValue(extractErrorMessage(error));
    }
});
const deleteConnection = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('connections/delete', async (id, { rejectWithValue })=>{
    try {
        await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].deleteConnection(id);
        return id;
    } catch (error) {
        return rejectWithValue(extractErrorMessage(error));
    }
});
const testConnection = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('connections/test', async (id, { rejectWithValue })=>{
    try {
        return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].testConnection(id);
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
const connectionSlice = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createSlice"])({
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
        }).addCase(testConnection.rejected, (state, action)=>{
            state.isLoading = false;
            state.error = ensureStringError(action.payload || 'Connection test failed');
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
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/store/slices/pipelineSlice.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
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
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/@reduxjs/toolkit/dist/redux-toolkit.modern.mjs [app-client] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api/client.ts [app-client] (ecmascript)");
;
;
const initialState = {
    pipelines: [],
    selectedPipeline: null,
    isLoading: false,
    error: null
};
const fetchPipelines = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/fetchAll', async (_, { rejectWithValue })=>{
    try {
        return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].getPipelines();
    } catch (error) {
        // Provide more helpful error messages for timeouts
        if (error.isTimeout) {
            return rejectWithValue('Request timeout: The server took too long to respond. This may indicate a database connection issue. Please check if MongoDB is running.');
        }
        if (error.isNetworkError) {
            return rejectWithValue('Network error: Cannot connect to the backend server. Please ensure it is running on http://localhost:8000');
        }
        return rejectWithValue(error.message || 'Failed to fetch pipelines');
    }
});
const fetchPipeline = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/fetchOne', async (id)=>{
    return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].getPipeline(id);
});
const createPipeline = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/create', async (pipelineData, { rejectWithValue })=>{
    try {
        return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].createPipeline(pipelineData);
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
const updatePipeline = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/update', async ({ id, data }, { rejectWithValue })=>{
    try {
        return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].updatePipeline(String(id), data);
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
const deletePipeline = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/delete', async (id, { rejectWithValue })=>{
    try {
        await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].deletePipeline(id);
        return id;
    } catch (error) {
        return rejectWithValue(error.response?.data?.detail || 'Failed to delete pipeline');
    }
});
const triggerPipeline = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/trigger', async ({ id, runType }, { rejectWithValue, dispatch })=>{
    try {
        const result = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].triggerPipeline(String(id), runType);
        // Refresh pipelines to get updated status
        dispatch(fetchPipelines());
        return result;
    } catch (error) {
        return rejectWithValue(error.response?.data?.detail || 'Failed to trigger pipeline');
    }
});
const pausePipeline = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/pause', async (id, { rejectWithValue, dispatch })=>{
    try {
        const result = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].pausePipeline(String(id));
        // Refresh pipelines to get updated status
        dispatch(fetchPipelines());
        return result;
    } catch (error) {
        return rejectWithValue(error.response?.data?.detail || 'Failed to pause pipeline');
    }
});
const stopPipeline = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/stop', async (id, { rejectWithValue, dispatch })=>{
    try {
        const result = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].stopPipeline(String(id));
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
const fetchPipelineStatus = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('pipelines/fetchStatus', async (id)=>{
    return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].getPipelineStatus(id);
});
const pipelineSlice = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createSlice"])({
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
            state.pipelines = action.payload;
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
        }).addCase(triggerPipeline.fulfilled, (state, action)=>{
            // Update pipeline status to active
            // The response has 'id' field, not 'pipeline_id'
            const pipelineId = action.payload.id || action.payload.pipeline_id;
            const pipeline = state.pipelines.find((p)=>p.id === pipelineId);
            if (pipeline) {
                pipeline.status = 'active';
            }
            if (state.selectedPipeline && state.selectedPipeline.id === pipelineId) {
                state.selectedPipeline.status = 'active';
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
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/store/slices/monitoringSlice.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
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
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/@reduxjs/toolkit/dist/redux-toolkit.modern.mjs [app-client] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api/client.ts [app-client] (ecmascript)");
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
const fetchReplicationEvents = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('monitoring/fetchEvents', async ({ pipelineId, skip, limit, todayOnly, startDate, endDate, tableName })=>{
    return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].getReplicationEvents(pipelineId, skip, limit, todayOnly || false, startDate, endDate, tableName);
});
const fetchMonitoringMetrics = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createAsyncThunk"])('monitoring/fetchMetrics', async ({ pipelineId, startTime, endTime })=>{
    // Convert to string if it's a number, or use as-is if it's already a string
    const id = typeof pipelineId === 'number' && !isNaN(pipelineId) ? pipelineId : String(pipelineId);
    // Don't proceed if ID is invalid
    if (!id || id === 'NaN' || id === 'undefined') {
        throw new Error('Invalid pipeline ID');
    }
    return await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].getMonitoringMetrics(id, startTime, endTime);
});
const monitoringSlice = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createSlice"])({
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
            state.events = action.payload;
        }).addCase(fetchReplicationEvents.rejected, (state, action)=>{
            state.isLoading = false;
            state.error = action.error.message || 'Failed to fetch events';
        }).addCase(fetchMonitoringMetrics.pending, (state)=>{
            state.isLoading = true;
        }).addCase(fetchMonitoringMetrics.fulfilled, (state, action)=>{
            state.isLoading = false;
            state.metrics = action.payload;
        }).addCase(fetchMonitoringMetrics.rejected, (state, action)=>{
            state.isLoading = false;
            state.error = action.error.message || 'Failed to fetch metrics';
        });
    }
});
const { setSelectedPipeline, addReplicationEvent, addMonitoringMetric, setRealTimeEnabled, clearEvents, clearError } = monitoringSlice.actions;
const __TURBOPACK__default__export__ = monitoringSlice.reducer;
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/store/slices/permissionSlice.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
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
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/@reduxjs/toolkit/dist/redux-toolkit.modern.mjs [app-client] (ecmascript) <locals>");
;
const initialState = {
    permissions: [],
    isLoading: false,
    error: null
};
const permissionSlice = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createSlice"])({
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
const hasPermission = (permission)=>(state)=>{
        return state.permissions.permissions.includes(permission);
    };
const hasAnyPermission = (permissions)=>(state)=>{
        return permissions.some((perm)=>state.permissions.permissions.includes(perm));
    };
const hasAllPermissions = (permissions)=>(state)=>{
        return permissions.every((perm)=>state.permissions.permissions.includes(perm));
    };
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/store/store.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Redux store configuration
 */ __turbopack_context__.s([
    "store",
    ()=>store
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/@reduxjs/toolkit/dist/redux-toolkit.modern.mjs [app-client] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$authSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/authSlice.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$connectionSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/connectionSlice.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$pipelineSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/pipelineSlice.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$monitoringSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/monitoringSlice.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/alertsSlice.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$permissionSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/permissionSlice.ts [app-client] (ecmascript)");
;
;
;
;
;
;
;
const store = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$reduxjs$2f$toolkit$2f$dist$2f$redux$2d$toolkit$2e$modern$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["configureStore"])({
    reducer: {
        auth: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$authSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"],
        connections: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$connectionSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"],
        pipelines: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$pipelineSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"],
        monitoring: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$monitoringSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"],
        alerts: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$alertsSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"],
        permissions: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$permissionSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"]
    }
});
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/websocket/client.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * WebSocket client for real-time monitoring
 */ __turbopack_context__.s([
    "wsClient",
    ()=>wsClient
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$socket$2e$io$2d$client$2f$build$2f$esm$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/socket.io-client/build/esm/index.js [app-client] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/store.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$monitoringSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/slices/monitoringSlice.ts [app-client] (ecmascript)");
;
;
;
const WS_URL = ("TURBOPACK compile-time value", "http://localhost:8000") || 'http://localhost:8000';
class WebSocketClient {
    socket = null;
    subscribedPipelines = new Set();
    isConnecting = false;
    connectionFailed = false;
    connect() {
        // Prevent multiple connection attempts
        if (this.socket?.connected) {
            return;
        }
        if (this.isConnecting) {
            return;
        }
        // If connection has previously failed, don't retry (backend may not have Socket.IO)
        if (this.connectionFailed) {
            return;
        }
        this.isConnecting = true;
        this.socket = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$socket$2e$io$2d$client$2f$build$2f$esm$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["io"])(WS_URL, {
            path: '/socket.io',
            transports: [
                'websocket',
                'polling'
            ],
            reconnection: false,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: 0,
            timeout: 5000,
            forceNew: false,
            autoConnect: true
        });
        this.socket.on('connect', ()=>{
            console.log('========================================');
            console.log('[Frontend] WEBSOCKET CONNECTED');
            console.log('========================================');
            console.log('[Frontend] Socket ID:', this.socket?.id);
            console.log('[Frontend] Previously subscribed pipelines:', Array.from(this.subscribedPipelines));
            this.isConnecting = false;
            this.connectionFailed = false; // Reset failure flag on successful connection
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
            if (reason === 'io server disconnect') {
                // Server disconnected, try to reconnect manually
                this.socket?.connect();
            }
        });
        this.socket.on('connect_error', (error)=>{
            // Suppress WebSocket connection errors - backend may not have Socket.IO configured
            // This is not critical for the application to function
            this.isConnecting = false;
            this.connectionFailed = true; // Mark as failed to prevent future attempts
            // Disable reconnection to prevent spam
            if (this.socket) {
                this.socket.io.reconnecting = false;
                // Disconnect to clean up
                this.socket.disconnect();
            }
        // Silently fail - WebSocket is optional for real-time updates
        // Don't log to console to avoid cluttering logs
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
                __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["store"].dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$monitoringSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["addReplicationEvent"])(data));
                console.log('[Frontend] ✓ Event added to Redux store');
                // Refresh events from API with correct parameters when new event is received
                // This ensures the events list is up-to-date with all parameters applied
                const state = __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["store"].getState();
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
                __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["store"].dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$monitoringSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["fetchReplicationEvents"])(fetchParams));
                // Show browser notification for new events
                if (("TURBOPACK compile-time value", "object") !== 'undefined' && 'Notification' in window && Notification.permission === 'granted') {
                    new Notification('CDC Event Captured', {
                        body: `${data.event_type?.toUpperCase() || 'EVENT'} on ${data.table_name || 'table'} - ${data.status || 'unknown'}`,
                        icon: '/icon-dark-32x32.png'
                    });
                }
            } catch (error) {
                console.error('Error handling replication event:', error);
            }
        });
        this.socket.on('monitoring_metric', (data)=>{
            try {
                console.log('Received monitoring metric:', data);
                __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["store"].dispatch((0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$slices$2f$monitoringSlice$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["addMonitoringMetric"])(data));
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
        return this.socket?.connected || false;
    }
}
const wsClient = new WebSocketClient();
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/providers/ReduxProvider.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Redux Provider component
 */ __turbopack_context__.s([
    "ReduxProvider",
    ()=>ReduxProvider
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$redux$2f$dist$2f$react$2d$redux$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/react-redux/dist/react-redux.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/store/store.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$websocket$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/websocket/client.ts [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
'use client';
;
;
;
;
function ReduxProvider({ children }) {
    _s();
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "ReduxProvider.useEffect": ()=>{
            // Connect WebSocket on mount
            __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$websocket$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["wsClient"].connect();
            // Cleanup on unmount
            return ({
                "ReduxProvider.useEffect": ()=>{
                    __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$websocket$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["wsClient"].disconnect();
                }
            })["ReduxProvider.useEffect"];
        }
    }["ReduxProvider.useEffect"], []);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$redux$2f$dist$2f$react$2d$redux$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Provider"], {
        store: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$store$2f$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["store"],
        children: children
    }, void 0, false, {
        fileName: "[project]/components/providers/ReduxProvider.tsx",
        lineNumber: 22,
        columnNumber: 10
    }, this);
}
_s(ReduxProvider, "OD7bBpZva5O2jO+Puf00hKivP7c=");
_c = ReduxProvider;
var _c;
__turbopack_context__.k.register(_c, "ReduxProvider");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/ui/use-toast.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "reducer",
    ()=>reducer,
    "toast",
    ()=>toast,
    "useToast",
    ()=>useToast
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var _s = __turbopack_context__.k.signature();
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
    _s();
    const [state, setState] = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"](memoryState);
    __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"]({
        "useToast.useEffect": ()=>{
            listeners.push(setState);
            return ({
                "useToast.useEffect": ()=>{
                    const index = listeners.indexOf(setState);
                    if (index > -1) {
                        listeners.splice(index, 1);
                    }
                }
            })["useToast.useEffect"];
        }
    }["useToast.useEffect"], [
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
_s(useToast, "SPWE98mLGnlsnNfIwu/IAKTSZtk=");
;
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/ui/toaster.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "Toaster",
    ()=>Toaster
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$use$2d$toast$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/ui/use-toast.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/x.js [app-client] (ecmascript) <export default as X>");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
function Toaster() {
    _s();
    const { toasts } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$use$2d$toast$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useToast"])();
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "fixed top-0 right-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:top-auto sm:right-0 sm:bottom-0 sm:flex-col md:max-w-[420px] pointer-events-none",
        children: toasts.map(function({ id, title, description, variant, ...props }) {
            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "pointer-events-auto mb-4 flex w-full flex-col items-start gap-2 overflow-hidden rounded-lg border p-4 shadow-lg transition-all data-[swipe=cancel]:translate-x-0 data-[swipe=end]:translate-x-[var(--radix-toast-swipe-end-x)] data-[swipe=move]:translate-x-[var(--radix-toast-swipe-move-x)] data-[swipe=move]:transition-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[swipe=end]:animate-out data-[state=closed]:fade-out-80 data-[state=closed]:slide-out-to-right-full data-[state=open]:slide-in-from-top-full data-[state=open]:sm:slide-in-from-bottom-full",
                style: {
                    backgroundColor: variant === "destructive" ? "rgba(239, 68, 68, 0.1)" : "rgba(6, 182, 212, 0.1)",
                    borderColor: variant === "destructive" ? "rgba(239, 68, 68, 0.3)" : "rgba(6, 182, 212, 0.3)"
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "grid gap-1 flex-1",
                        children: [
                            title && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
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
                            description && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
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
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        onClick: ()=>{
                        // Auto-dismiss after showing
                        },
                        className: "absolute right-2 top-2 rounded-md p-1 opacity-70 transition-opacity hover:opacity-100",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
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
_s(Toaster, "1YTCnXrq2qRowe0H/LBWLjtXoYc=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$use$2d$toast$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useToast"]
    ];
});
_c = Toaster;
var _c;
__turbopack_context__.k.register(_c, "Toaster");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=_dd2a0eb5._.js.map