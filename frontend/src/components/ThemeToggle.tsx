import { IconButton } from "@chakra-ui/react";
import { useState } from "react";

interface ThemeToggleProps {
    colorMode: "light" | "dark";
    onToggle: () => void;
    currentColors: {
        text: string;
    };
}

export const ThemeToggle = ({
    colorMode,
    onToggle,
    currentColors,
}: ThemeToggleProps) => {
    const [isAnimating, setIsAnimating] = useState(false);

    const handleToggle = () => {
        setIsAnimating(true);
        onToggle();
        setTimeout(() => setIsAnimating(false), 600);
    };

    return (
        <IconButton
            aria-label="Toggle dark mode"
            onClick={handleToggle}
            size="lg"
            variant="ghost"
            fontSize="2xl"
            color={currentColors.text}
            position="relative"
            overflow="visible"
            _hover={{
                bg: colorMode === "dark" ? "#292e42" : "#b8bac4",
                transform: "rotate(20deg) scale(1.1)",
            }}
            _active={{
                transform: "rotate(360deg) scale(0.95)",
            }}
            transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            css={{
                "@keyframes sparkle": {
                    "0%, 100%": {
                        opacity: 0,
                        transform: "scale(0) rotate(0deg)",
                    },
                    "50%": {
                        opacity: 1,
                        transform: "scale(1) rotate(180deg)",
                    },
                },
                "&::before": isAnimating
                    ? {
                          content: '""',
                          position: "absolute",
                          width: "100%",
                          height: "100%",
                          borderRadius: "50%",
                          background:
                              colorMode === "dark"
                                  ? "radial-gradient(circle, rgba(122, 162, 247, 0.4) 0%, transparent 70%)"
                                  : "radial-gradient(circle, rgba(152, 84, 241, 0.4) 0%, transparent 70%)",
                          animation: "sparkle 0.6s ease-out",
                          pointerEvents: "none",
                      }
                    : {},
            }}
        >
            <span
                style={{
                    display: "inline-block",
                    transition: "transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                    transform: isAnimating
                        ? "scale(1.3) rotate(360deg)"
                        : "scale(1)",
                }}
            >
                {colorMode === "light" ? "🌙" : "☀️"}
            </span>
        </IconButton>
    );
};
