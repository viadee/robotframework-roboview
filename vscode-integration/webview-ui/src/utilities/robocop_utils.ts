import { RobocopMessage } from "../types/robocop";

export function deduplicateRobocopMessages(
  messages: RobocopMessage[],
): RobocopMessage[] {
  const seen = new Map<string, RobocopMessage>();

  messages.forEach((message) => {
    const key = message.message_id;

    if (!seen.has(key)) {
      seen.set(key, message);
    }
  });

  return Array.from(seen.values());
}

export function filterMessagesByType(
  allMessages: RobocopMessage[],
  filterType: string,
): RobocopMessage[] {
  let result: RobocopMessage[];

  switch (filterType) {
    case "all":
      result = allMessages;
      break;
    case "arguments":
      result = allMessages.filter((msg) => msg.category === "Arguments");
      break;
    case "comments":
      result = allMessages.filter((msg) => msg.category === "Comments");
      break;
    case "documentation":
      result = allMessages.filter((msg) => msg.category === "Documentation");
      break;
    case "duplication":
      result = allMessages.filter((msg) => msg.category === "Duplication");
      break;
    case "errors":
      result = allMessages.filter((msg) => msg.category === "Errors");
      break;
    case "imports":
      result = allMessages.filter((msg) => msg.category === "Imports");
      break;
    case "keywords":
      result = allMessages.filter((msg) => msg.category === "Keywords");
      break;
    case "lengths":
      result = allMessages.filter((msg) => msg.category === "Lengths");
      break;
    case "miscellaneous":
      result = allMessages.filter((msg) => msg.category === "Miscellaneous");
      break;
    case "naming":
      result = allMessages.filter((msg) => msg.category === "Naming");
      break;
    case "order":
      result = allMessages.filter((msg) => msg.category === "Order");
      break;
    case "spacing":
      result = allMessages.filter((msg) => msg.category === "Spacing");
      break;
    case "tags":
      result = allMessages.filter((msg) => msg.category === "Tags");
      break;
    case "variables":
      result = allMessages.filter((msg) => msg.category === "Variables");
      break;
    case "annotations":
      result = allMessages.filter((msg) => msg.category === "Annotations");
      break;
    case "deprecated":
      result = allMessages.filter((msg) => msg.category === "Deprecated");
      break;
    case "info":
      result = allMessages.filter((msg) => msg.severity === "I");
      break;
    case "warning":
      result = allMessages.filter((msg) => msg.severity === "W");
      break;
    case "error":
      result = allMessages.filter((msg) => msg.severity === "E");
      break;
    default:
      result = allMessages;
  }

  return deduplicateRobocopMessages(result);
}

/**
 * Filter messages by search term
 */
export function filterMessagesBySearch(
  messages: RobocopMessage[],
  searchTerm: string,
): RobocopMessage[] {
  if (!searchTerm.trim()) return messages;

  const lowerSearch = searchTerm.toLowerCase();
  return messages.filter(
    (msg) =>
      msg.message.toLowerCase().includes(lowerSearch) ||
      msg.rule_message.toLowerCase().includes(lowerSearch) ||
      msg.file_name.toLowerCase().includes(lowerSearch) ||
      msg.source.toLowerCase().includes(lowerSearch),
  );
}

/**
 * Sort messages
 */
export function sortRobocopMessages(
  messages: RobocopMessage[],
  sortBy: string,
): RobocopMessage[] {
  const sorted = [...messages];

  switch (sortBy) {
    case "name_asc":
      return sorted.sort((a, b) => a.rule_id.localeCompare(b.rule_id));
    case "name_desc":
      return sorted.sort((a, b) => b.rule_id.localeCompare(a.rule_id));
    case "severity_high":
      // E > W > I
      const severityOrder = { E: 3, W: 2, I: 1 };
      return sorted.sort(
        (a, b) =>
          (severityOrder[b.severity as keyof typeof severityOrder] || 0) -
          (severityOrder[a.severity as keyof typeof severityOrder] || 0),
      );
    case "severity_low":
      // I > W > E
      const severityOrderLow = { E: 3, W: 2, I: 1 };
      return sorted.sort(
        (a, b) =>
          (severityOrderLow[a.severity as keyof typeof severityOrderLow] || 0) -
          (severityOrderLow[b.severity as keyof typeof severityOrderLow] || 0),
      );
    default:
      return sorted;
  }
}
