import { useQuery } from "@tanstack/react-query";
import { getReadiness } from "../api/health";
export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: getReadiness,
    refetchInterval: 5000,
    retry: false,
    staleTime: 0,
  });
}
