import { useMutation } from "@tanstack/react-query";
import { askQuestion } from "../api/chat";
import { toast } from "sonner";

export function useChat() {
  const chat = useMutation({
    mutationFn: askQuestion,
    onError: (error) => {
      const status = error.response?.status;
      toast.error(
        error.message === "The request timed out."
          ? "The model took too long to respond. Ollama may still be loading the model."
          : status === 503
          ? "The selected provider is unavailable."
          : status === 422
            ? "Unable to generate a response for this request."
            : "Unable to generate response."
      );
    },
  });

  return {
    ...chat,
    askQuestion: chat.mutateAsync,
    answer: chat.data,
    isLoading: chat.isPending,
    isError: chat.isError,
  };
}
