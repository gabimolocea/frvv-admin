import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import Navbar from './components/navbar/Navbar';
import App from './App.jsx';
import { BrowserRouter } from 'react-router-dom';

const rootElement = document.getElementById('root');

if (rootElement) {
  createRoot(rootElement).render(
    <React.StrictMode>
      <BrowserRouter>
        <Navbar content={<App />} />
      </BrowserRouter>
    </React.StrictMode>
  );
} else {
  console.error('Root element not found. Please check your HTML file.');
}