import React from "react";
import Dashboard from "./components/Dashboard";
import { Toaster } from "sonner";
import "./App.css";

function App() {
  return (
    <>
      <Dashboard />
      <Toaster position="top-right" richColors />
    </>
  );
}

export default App;
