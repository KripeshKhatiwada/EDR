import { useEffect, useState } from "react";
import api from "../services/api";

function Dashboard() {
    const [telemetry, setTelemetry] = useState([]);

    useEffect(() => {
        api.get("http://127.0.0.1:8000/telemetry")
            .then((res) => {
                console.log("DATA:", res.data);
                setTelemetry(res.data);
            })
            .catch((err) => {
                console.log("ERROR:", err);
            });
    }, []);

    return (
        <div>
            <h1>EDR Dashboard</h1>

            {telemetry.map((item) => (
                <div key={item.id}>
                    <h3>{item.hostname}</h3>

                    <p>CPU: {item.cpu_percent}%</p>

                    <p>Memory: {item.memory_percent}%</p>

                    <p>Disk: {item.disk_percent}%</p>

                    <hr />
                </div>
            ))}
        </div>
    );
}

export default Dashboard;