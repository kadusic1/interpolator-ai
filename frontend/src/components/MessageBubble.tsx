import React from "react";
import clsx from "clsx";
import { Bot, User } from "lucide-react";
import type { Message } from "../types";
import ResultCard from "./ResultCard";

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.type === "user";

  return (
    <div
      className={clsx(
        "flex w-full gap-4 p-4 md:px-8",
        isUser ? "flex-row-reverse" : "flex-row",
      )}
    >
      {/* Avatar */}
      <div
        className={clsx(
          "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
          isUser ? "bg-gray-200 text-gray-600" : "bg-blue-100 text-blue-600",
        )}
      >
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>

      {/* Content */}
      <div
        className={clsx(
          "flex flex-col max-w-[85%]",
          isUser ? "items-end" : "items-start",
        )}
      >
        <div className="text-sm font-medium text-gray-500 mb-1">
          {isUser ? "You" : "Interpolator"}
        </div>

        {typeof message.content === "string" ? (
          <div
            className={clsx(
              "prose prose-sm max-w-none rounded-2xl px-5 py-3",
              isUser
                ? "bg-gray-200 text-gray-900 rounded-tr-none"
                : "bg-transparent text-gray-800 px-0 py-0",
            )}
          >
            {/* Simple text rendering for now, could act as markdown later */}
            <p className="whitespace-pre-wrap leading-relaxed">
              {message.content}
            </p>
          </div>
        ) : (
          <div className="w-full space-y-6">
            {message.content.map((item, idx) => (
              <ResultCard key={idx} data={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
