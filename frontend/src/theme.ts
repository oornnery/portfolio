import { createSystem, defaultConfig } from "@chakra-ui/react";

export const system = createSystem(defaultConfig, {
    theme: {
        tokens: {
            colors: {
                // Tokyo Night Color Palette
                tokyo: {
                    bg: { value: "#1a1b26" },
                    bgDark: { value: "#16161e" },
                    bgHighlight: { value: "#292e42" },
                    terminal: { value: "#16161e" },
                    fg: { value: "#c0caf5" },
                    fgDark: { value: "#a9b1d6" },
                    fgGutter: { value: "#3b4261" },
                    dark3: { value: "#545c7e" },
                    comment: { value: "#565f89" },
                    dark5: { value: "#737aa2" },
                    blue0: { value: "#3d59a1" },
                    blue: { value: "#7aa2f7" },
                    cyan: { value: "#7dcfff" },
                    blue1: { value: "#2ac3de" },
                    blue2: { value: "#0db9d7" },
                    blue5: { value: "#89ddff" },
                    blue6: { value: "#b4f9f8" },
                    blue7: { value: "#394b70" },
                    magenta: { value: "#bb9af7" },
                    magenta2: { value: "#ff007c" },
                    purple: { value: "#9d7cd8" },
                    orange: { value: "#ff9e64" },
                    yellow: { value: "#e0af68" },
                    green: { value: "#9ece6a" },
                    green1: { value: "#73daca" },
                    green2: { value: "#41a6b5" },
                    teal: { value: "#1abc9c" },
                    red: { value: "#f7768e" },
                    red1: { value: "#db4b4b" },
                },
                // Light mode colors (Tokyo Night Day) - Enhanced contrast
                tokyoDay: {
                    bg: { value: "#d5d6db" },
                    bgDark: { value: "#e9e9ed" },
                    bgHighlight: { value: "#b8bac4" },
                    fg: { value: "#33467c" },
                    fgDark: { value: "#0f4b6e" },
                    comment: { value: "#565a6e" },
                    blue: { value: "#2e7de9" },
                    cyan: { value: "#007197" },
                    magenta: { value: "#9854f1" },
                    orange: { value: "#b15c00" },
                    yellow: { value: "#8c6c3e" },
                    green: { value: "#2d7a6e" },
                    red: { value: "#c73866" },
                    teal: { value: "#007197" },
                },
            },
            animations: {
                "spin-slow": {
                    value: "spin 3s linear infinite",
                },
                "fade-in": {
                    value: "fadeIn 0.5s ease-in-out",
                },
                "slide-in": {
                    value: "slideIn 0.3s ease-out",
                },
            },
        },
        keyframes: {
            fadeIn: {
                from: { opacity: "0" },
                to: { opacity: "1" },
            },
            slideIn: {
                from: {
                    opacity: "0",
                    transform: "translateY(-10px)",
                },
                to: {
                    opacity: "1",
                    transform: "translateY(0)",
                },
            },
        },
    },
});
