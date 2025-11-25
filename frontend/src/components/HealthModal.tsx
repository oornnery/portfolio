import {
    VStack,
    HStack,
    Text,
    Badge,
    Box,
    Spinner,
    Dialog,
} from "@chakra-ui/react";
import type { PingEntry } from "../hooks/useHealthMonitor";

interface HealthModalProps {
    isOpen: boolean;
    onClose: () => void;
    service: "frontend" | "backend";
    colorMode: "light" | "dark";
    pingHistory: PingEntry[];
    statistics: {
        successCount: number;
        errorCount: number;
        avgResponseTime: number;
        totalPings: number;
    };
    currentStatus: "Online" | "Offline";
}

export const HealthModal = ({
    isOpen,
    onClose,
    service,
    colorMode,
    pingHistory,
    statistics,
    currentStatus,
}: HealthModalProps) => {
    const colors = {
        light: {
            bg: "#d5d6db",
            cardBg: "#e9e9ed",
            text: "#33467c",
            textSecondary: "#565a6e",
            border: "#9699a3",
        },
        dark: {
            bg: "#1a1b26",
            cardBg: "#16161e",
            text: "#c0caf5",
            textSecondary: "#a9b1d6",
            border: "#292e42",
        },
    };

    const currentColors = colors[colorMode];

    const getStatusColor = (status: "success" | "error") => {
        if (status === "success") {
            return colorMode === "dark" ? "#9ece6a" : "#2d7a6e";
        }
        return colorMode === "dark" ? "#f7768e" : "#c73866";
    };

    return (
        <Dialog.Root
            open={isOpen}
            onOpenChange={(details) => {
                if (!details.open) {
                    onClose();
                }
            }}
            size="lg"
        >
            <Dialog.Backdrop />
            <Dialog.Positioner>
                <Dialog.Content
                    bg={currentColors.bg}
                    color={currentColors.text}
                    borderColor={currentColors.border}
                    borderWidth="1px"
                    maxW="600px"
                >
                    <Dialog.Header
                        borderBottomWidth="1px"
                        borderColor={currentColors.border}
                        pb={3}
                    >
                        <HStack gap={2}>
                            <Dialog.Title fontSize="lg" fontWeight="semibold">
                                {service === "frontend" ? "📊" : "🖥️"}{" "}
                                {service === "frontend"
                                    ? "Frontend"
                                    : "Backend"}{" "}
                                Health Monitor
                            </Dialog.Title>
                            <Spinner size="sm" color={currentColors.text} />
                            <Badge
                                bg={
                                    currentStatus === "Online"
                                        ? colorMode === "dark"
                                            ? "#9ece6a"
                                            : "#2d7a6e"
                                        : colorMode === "dark"
                                          ? "#f7768e"
                                          : "#c73866"
                                }
                                color={
                                    colorMode === "dark" ? "#1a1b26" : "#ffffff"
                                }
                                px={2}
                                py={1}
                                borderRadius="md"
                                fontSize="xs"
                            >
                                {currentStatus}
                            </Badge>
                        </HStack>
                    </Dialog.Header>

                    <Dialog.CloseTrigger />

                    <Dialog.Body py={4}>
                        <VStack align="stretch" gap={4}>
                            {/* Statistics */}
                            <HStack
                                p={4}
                                bg={currentColors.cardBg}
                                borderRadius="lg"
                                justify="space-around"
                            >
                                <VStack gap={1}>
                                    <Text
                                        fontSize="xs"
                                        color={currentColors.textSecondary}
                                    >
                                        Success
                                    </Text>
                                    <Text
                                        fontSize="2xl"
                                        fontWeight="bold"
                                        color="#9ece6a"
                                    >
                                        {statistics.successCount}
                                    </Text>
                                </VStack>
                                <VStack gap={1}>
                                    <Text
                                        fontSize="xs"
                                        color={currentColors.textSecondary}
                                    >
                                        Errors
                                    </Text>
                                    <Text
                                        fontSize="2xl"
                                        fontWeight="bold"
                                        color="#f7768e"
                                    >
                                        {statistics.errorCount}
                                    </Text>
                                </VStack>
                                <VStack gap={1}>
                                    <Text
                                        fontSize="xs"
                                        color={currentColors.textSecondary}
                                    >
                                        Avg Time
                                    </Text>
                                    <Text
                                        fontSize="2xl"
                                        fontWeight="bold"
                                        color={currentColors.text}
                                    >
                                        {statistics.avgResponseTime}ms
                                    </Text>
                                </VStack>
                                <VStack gap={1}>
                                    <Text
                                        fontSize="xs"
                                        color={currentColors.textSecondary}
                                    >
                                        Total
                                    </Text>
                                    <Text
                                        fontSize="2xl"
                                        fontWeight="bold"
                                        color={currentColors.text}
                                    >
                                        {statistics.totalPings}
                                    </Text>
                                </VStack>
                            </HStack>

                            {/* Ping History */}
                            <Box>
                                <Text
                                    fontSize="sm"
                                    fontWeight="semibold"
                                    mb={2}
                                    color={currentColors.text}
                                >
                                    Ping History (Last 100)
                                </Text>
                                <VStack
                                    align="stretch"
                                    gap={2}
                                    maxH="400px"
                                    overflowY="auto"
                                    pr={2}
                                    css={{
                                        "&::-webkit-scrollbar": {
                                            width: "8px",
                                        },
                                        "&::-webkit-scrollbar-track": {
                                            background:
                                                colorMode === "dark"
                                                    ? "#1a1b26"
                                                    : "#d5d6db",
                                            borderRadius: "4px",
                                        },
                                        "&::-webkit-scrollbar-thumb": {
                                            background:
                                                colorMode === "dark"
                                                    ? "#292e42"
                                                    : "#9699a3",
                                            borderRadius: "4px",
                                        },
                                    }}
                                >
                                    {pingHistory.length === 0 ? (
                                        <Text
                                            color={currentColors.textSecondary}
                                            textAlign="center"
                                            py={4}
                                        >
                                            Starting monitoring...
                                        </Text>
                                    ) : (
                                        pingHistory.map((ping, index) => (
                                            <HStack
                                                key={`${ping.timestamp}-${index}`}
                                                p={3}
                                                bg={currentColors.cardBg}
                                                borderRadius="md"
                                                justify="space-between"
                                                borderLeftWidth="3px"
                                                borderLeftColor={getStatusColor(
                                                    ping.status,
                                                )}
                                                transition="all 0.2s"
                                                _hover={{
                                                    transform:
                                                        "translateX(4px)",
                                                }}
                                            >
                                                <HStack gap={3}>
                                                    <Text
                                                        fontSize="xs"
                                                        color={
                                                            currentColors.textSecondary
                                                        }
                                                        fontFamily="monospace"
                                                        minW="80px"
                                                    >
                                                        {ping.timestamp}
                                                    </Text>
                                                    <Badge
                                                        bg={getStatusColor(
                                                            ping.status,
                                                        )}
                                                        color={
                                                            colorMode === "dark"
                                                                ? "#1a1b26"
                                                                : "#ffffff"
                                                        }
                                                        fontSize="xs"
                                                        px={2}
                                                        py={1}
                                                        borderRadius="md"
                                                    >
                                                        {ping.status ===
                                                        "success"
                                                            ? "✓ OK"
                                                            : "✗ FAIL"}
                                                    </Badge>
                                                </HStack>
                                                <HStack gap={2}>
                                                    {ping.responseTime && (
                                                        <Text
                                                            fontSize="xs"
                                                            color={
                                                                currentColors.textSecondary
                                                            }
                                                            fontFamily="monospace"
                                                        >
                                                            {ping.responseTime}
                                                            ms
                                                        </Text>
                                                    )}
                                                    {ping.message && (
                                                        <Text
                                                            fontSize="xs"
                                                            color={
                                                                currentColors.textSecondary
                                                            }
                                                        >
                                                            {ping.message}
                                                        </Text>
                                                    )}
                                                </HStack>
                                            </HStack>
                                        ))
                                    )}
                                </VStack>
                            </Box>
                        </VStack>
                    </Dialog.Body>
                </Dialog.Content>
            </Dialog.Positioner>
        </Dialog.Root>
    );
};
