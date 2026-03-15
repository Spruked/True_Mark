import React from "react";
import { createRoot } from "react-dom/client";
import ChatBubble from "./ChatBubble";
import "./styles.css";

const root = createRoot(document.getElementById("root"));
root.render(<ChatBubble />);
