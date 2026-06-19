import { useState, useEffect } from "react";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";

function App() {
    const [loggedIn, setLoggedIn] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (token) {
            setLoggedIn(true);
        }
    }, []);

    return loggedIn ? (
        <Dashboard />
    ) : (
        <Login onLogin={() => setLoggedIn(true)} />
    );
}

export default App;