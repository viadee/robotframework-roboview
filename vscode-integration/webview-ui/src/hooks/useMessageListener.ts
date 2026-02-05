import { useEffect } from "react";

export function useMessageListener(
  handlers: Record<string, (message: any) => void>,
) {
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      const message = event.data;
      const handler = handlers[message.command];
      if (handler) {
        handler(message);
      }
    };

    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, [handlers]);
}
