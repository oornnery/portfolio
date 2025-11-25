import { useEffect, useState } from "react";
import {
    Box,
    Heading,
    Text,
    Badge,
    Container,
    VStack,
    HStack,
    Link,
} from "@chakra-ui/react";
import { ThemeToggle } from "./components/ThemeToggle";
import { HealthModal } from "./components/HealthModal";
import { useHealthMonitor } from "./hooks/useHealthMonitor";

function App() {
    const [isTransitioning, setIsTransitioning] = useState(false);
    const [healthModalOpen, setHealthModalOpen] = useState(false);
    const [selectedService, setSelectedService] = useState<
        "frontend" | "backend"
    >("backend");

    // Monitoramento contínuo desde o início
    const frontendMonitor = useHealthMonitor({ service: "frontend" });
    const backendMonitor = useHealthMonitor({ service: "backend" });

    // Inicializar color mode diretamente sem useEffect
    const getInitialColorMode = (): "light" | "dark" => {
        const savedMode = localStorage.getItem("chakra-ui-color-mode") as
            | "light"
            | "dark"
            | null;
        if (savedMode) return savedMode;

        const prefersDark = window.matchMedia(
            "(prefers-color-scheme: dark)",
        ).matches;
        return prefersDark ? "dark" : "light";
    };

    const [colorMode, setColorMode] = useState<"light" | "dark">(
        getInitialColorMode,
    );

    const toggleColorMode = () => {
        setIsTransitioning(true);

        setTimeout(() => {
            const newMode = colorMode === "light" ? "dark" : "light";
            setColorMode(newMode);
            document.documentElement.classList.toggle(
                "dark",
                newMode === "dark",
            );
            localStorage.setItem("chakra-ui-color-mode", newMode);
        }, 150);

        setTimeout(() => {
            setIsTransitioning(false);
        }, 450);
    };

    // Aplicar a classe dark no mount
    useEffect(() => {
        document.documentElement.classList.toggle("dark", colorMode === "dark");
    }, [colorMode]);

    const openHealthModal = (service: "frontend" | "backend") => {
        setSelectedService(service);
        setHealthModalOpen(true);
    };

    // Tokyo Night color palette
    const colors = {
        light: {
            bg: "#d5d6db",
            cardBg: "#e9e9ed",
            text: "#33467c",
            textSecondary: "#565a6e",
            border: "#9699a3",
            shadow: "rgba(51, 70, 124, 0.15)",
        },
        dark: {
            bg: "#1a1b26",
            cardBg: "#16161e",
            text: "#c0caf5",
            textSecondary: "#a9b1d6",
            border: "#292e42",
            shadow: "rgba(0, 0, 0, 0.3)",
        },
    };

    const currentColors = colors[colorMode];

    return (
        <>
            {/* Smooth transition overlay */}
            <Box
                position="fixed"
                top={0}
                left={0}
                right={0}
                bottom={0}
                bg={colorMode === "dark" ? "#1a1b26" : "#e1e2e7"}
                opacity={isTransitioning ? 0.3 : 0}
                pointerEvents="none"
                transition="opacity 0.3s ease-in-out"
                zIndex={9999}
            />

            <Box
                minH="100vh"
                bg={currentColors.bg}
                color={currentColors.text}
                className="theme-transition"
            >
                <Container maxW="container.xl" centerContent py={10}>
                    <VStack gap={8} w="full">
                        <HStack justify="space-between" w="full">
                            <Heading
                                bgGradient={
                                    colorMode === "dark"
                                        ? "linear(to-r, #7aa2f7, #bb9af7)"
                                        : "linear(to-r, #2e7de9, #9854f1)"
                                }
                                bgClip="text"
                                fontSize={{ base: "2xl", md: "4xl" }}
                                fontWeight="bold"
                            >
                                Portfolio Full Stack
                            </Heading>
                            <ThemeToggle
                                colorMode={colorMode}
                                onToggle={toggleColorMode}
                                currentColors={currentColors}
                            />
                        </HStack>

                        <Box
                            p={8}
                            borderWidth="2px"
                            borderRadius="xl"
                            bg={currentColors.cardBg}
                            borderColor={currentColors.border}
                            w="full"
                            maxW="lg"
                            boxShadow={`0 10px 30px ${currentColors.shadow}`}
                            backdropFilter="blur(10px)"
                            _hover={{
                                transform: "translateY(-4px)",
                                boxShadow: `0 15px 40px ${currentColors.shadow}`,
                            }}
                            transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                        >
                            <Heading
                                fontSize="2xl"
                                mb={6}
                                color={currentColors.text}
                                fontWeight="semibold"
                            >
                                🚀 Status do Sistema
                            </Heading>
                            <VStack align="stretch" gap={4}>
                                <HStack
                                    justify="space-between"
                                    p={4}
                                    borderRadius="lg"
                                    bg={
                                        colorMode === "dark"
                                            ? "#1f2335"
                                            : "#dddee3"
                                    }
                                    transition="all 0.2s"
                                    cursor="pointer"
                                    onClick={() => openHealthModal("frontend")}
                                    _hover={{
                                        bg:
                                            colorMode === "dark"
                                                ? "#292e42"
                                                : "#cfd0d8",
                                        transform: "translateX(4px)",
                                    }}
                                >
                                    <HStack>
                                        <Text
                                            fontSize="lg"
                                            fontWeight="medium"
                                            color={currentColors.text}
                                        >
                                            Frontend
                                        </Text>
                                    </HStack>
                                    <Badge
                                        colorScheme="green"
                                        fontSize="md"
                                        px={3}
                                        py={1}
                                        borderRadius="full"
                                        bg={
                                            frontendMonitor.currentStatus ===
                                            "Online"
                                                ? colorMode === "dark"
                                                    ? "#9ece6a"
                                                    : "#2d7a6e"
                                                : colorMode === "dark"
                                                  ? "#f7768e"
                                                  : "#c73866"
                                        }
                                        color={
                                            colorMode === "dark"
                                                ? "#1a1b26"
                                                : "#ffffff"
                                        }
                                    >
                                        ● {frontendMonitor.currentStatus}
                                    </Badge>
                                </HStack>

                                <HStack
                                    justify="space-between"
                                    p={4}
                                    borderRadius="lg"
                                    bg={
                                        colorMode === "dark"
                                            ? "#1f2335"
                                            : "#dddee3"
                                    }
                                    transition="all 0.2s"
                                    cursor="pointer"
                                    onClick={() => openHealthModal("backend")}
                                    _hover={{
                                        bg:
                                            colorMode === "dark"
                                                ? "#292e42"
                                                : "#cfd0d8",
                                        transform: "translateX(4px)",
                                    }}
                                >
                                    <HStack>
                                        <Text
                                            fontSize="lg"
                                            fontWeight="medium"
                                            color={currentColors.text}
                                        >
                                            Backend
                                        </Text>
                                    </HStack>
                                    <Badge
                                        colorScheme={
                                            backendMonitor.currentStatus ===
                                            "Online"
                                                ? "green"
                                                : "red"
                                        }
                                        fontSize="md"
                                        px={3}
                                        py={1}
                                        borderRadius="full"
                                        bg={
                                            backendMonitor.currentStatus ===
                                            "Online"
                                                ? colorMode === "dark"
                                                    ? "#9ece6a"
                                                    : "#2d7a6e"
                                                : colorMode === "dark"
                                                  ? "#f7768e"
                                                  : "#c73866"
                                        }
                                        color={
                                            colorMode === "dark"
                                                ? "#1a1b26"
                                                : "#ffffff"
                                        }
                                    >
                                        ● {backendMonitor.currentStatus}
                                    </Badge>
                                </HStack>
                            </VStack>
                        </Box>

                        {/* Additional info card */}
                        <Box
                            p={6}
                            borderRadius="lg"
                            bg={currentColors.cardBg}
                            borderWidth="1px"
                            borderColor={currentColors.border}
                            w="full"
                            maxW="lg"
                            opacity={0.8}
                            _hover={{ opacity: 1 }}
                            transition="all 0.3s"
                        >
                            <Text
                                fontSize="sm"
                                color={currentColors.textSecondary}
                                textAlign="center"
                            >
                                Made with ❤️ by{" "}
                                <Link
                                    href="https://github.com/oornnery/portfolio"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    fontWeight="semibold"
                                    color={
                                        colorMode === "dark"
                                            ? "#7aa2f7"
                                            : "#2e7de9"
                                    }
                                    _hover={{
                                        textDecoration: "underline",
                                    }}
                                >
                                    @oornnery
                                </Link>
                            </Text>
                        </Box>
                    </VStack>
                </Container>
            </Box>

            {/* Health Monitor Modal */}
            <HealthModal
                isOpen={healthModalOpen}
                onClose={() => setHealthModalOpen(false)}
                service={selectedService}
                colorMode={colorMode}
                pingHistory={
                    selectedService === "frontend"
                        ? frontendMonitor.pingHistory
                        : backendMonitor.pingHistory
                }
                statistics={
                    selectedService === "frontend"
                        ? frontendMonitor.statistics
                        : backendMonitor.statistics
                }
                currentStatus={
                    selectedService === "frontend"
                        ? frontendMonitor.currentStatus
                        : backendMonitor.currentStatus
                }
            />
        </>
    );
}

export default App;
