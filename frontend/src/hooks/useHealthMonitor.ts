import { useEffect, useRef, useState } from "react";
import axios from "axios";

export interface PingEntry {
    timestamp: string;
    status: "success" | "error";
    responseTime?: number;
    message?: string;
}

interface UseHealthMonitorProps {
    service: "frontend" | "backend";
    enabled?: boolean;
}

export const useHealthMonitor = ({
    service,
    enabled = true,
}: UseHealthMonitorProps) => {
    const [pingHistory, setPingHistory] = useState<PingEntry[]>([]);
    const [currentStatus, setCurrentStatus] = useState<"Online" | "Offline">(
        "Online",
    );
    const intervalRef = useRef<number | null>(null);

    useEffect(() => {
        if (!enabled) {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
            return;
        }

        const getServiceUrl = () => {
            if (service === "frontend") {
                return window.location.origin + "/health.json";
            }
            return "http://localhost:8000/health";
        };

        const performPing = async () => {
            const startTime = performance.now();
            try {
                const response = await axios.get(getServiceUrl(), {
                    timeout: 5000,
                });
                const endTime = performance.now();
                const responseTime = Math.round(endTime - startTime);

                const entry: PingEntry = {
                    timestamp: new Date().toLocaleTimeString(),
                    status: "success",
                    responseTime,
                    message: response.data.message || "OK",
                };

                setPingHistory((prev) => [entry, ...prev].slice(0, 100)); // Keep last 100
                setCurrentStatus("Online");
            } catch {
                const entry: PingEntry = {
                    timestamp: new Date().toLocaleTimeString(),
                    status: "error",
                    message: "Failed to connect",
                };

                setPingHistory((prev) => [entry, ...prev].slice(0, 100));
                setCurrentStatus("Offline");
            }
        };

        // Primeira checagem imediata
        performPing();

        // Depois a cada 1 segundo
        const interval = window.setInterval(() => {
            performPing();
        }, 1000);

        intervalRef.current = interval;

        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
        };
    }, [service, enabled]);

    const getStatistics = () => {
        const successCount = pingHistory.filter(
            (p) => p.status === "success",
        ).length;
        const errorCount = pingHistory.filter(
            (p) => p.status === "error",
        ).length;
        const avgResponseTime =
            pingHistory.length > 0
                ? Math.round(
                      pingHistory
                          .filter((p) => p.responseTime)
                          .reduce((acc, p) => acc + (p.responseTime || 0), 0) /
                          pingHistory.filter((p) => p.responseTime).length,
                  )
                : 0;

        return {
            successCount,
            errorCount,
            avgResponseTime,
            totalPings: pingHistory.length,
        };
    };

    return {
        pingHistory,
        currentStatus,
        statistics: getStatistics(),
    };
};
