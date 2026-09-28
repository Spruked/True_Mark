import React from "react";
import { createRoot } from "react-dom/client";
import HumanSupportBubble from "./HumanSupportBubble";
import "./styles.css";

const root = createRoot(document.getElementById("root"));
root.render(<HumanSupportBubble visible={false} />);
