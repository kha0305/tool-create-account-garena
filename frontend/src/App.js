import { useState } from "react";
import "@/App.css";
import { HashRouter, Routes, Route } from "react-router-dom";
import Dashboard from "@/components/Dashboard";
import { Toaster } from "@/components/ui/sonner";

function App() {
  return (
    <div className="App">
      <HashRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </HashRouter>
      <Toaster position="top-right" />
    </div>
  );
}

export default App;