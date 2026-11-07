import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 50000,
      retry: 1,
    }
  },
});

export { QueryClientProvider };
