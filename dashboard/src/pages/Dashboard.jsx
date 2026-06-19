import { useEffect, useState } from "react";
import api from "../services/api";

function Dashboard() {
    const [telemetry, setTelemetry] = useState([]);
    const [processes, setProcesses] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [ports, setPorts] = useState([]);
    const [files, setFiles] = useState([]);
    const [hosts, setHosts] = useState([]);

    useEffect(() => {

        api.get("http://127.0.0.1:8000/telemetry")
            .then((res) => {
                console.log("TELEMETRY:", res.data);
                setTelemetry(res.data);
            })
            .catch((err) => console.log(err));

        api.get("http://127.0.0.1:8000/processes")
            .then((res) => {
                console.log("PROCESSES:", res.data);
                setProcesses(res.data);
            })
            .catch((err) => console.log(err));

        api.get("http://127.0.0.1:8000/alerts")
            .then((res) => {
                console.log("ALERTS:", res.data);
                setAlerts(res.data);
            })
            .catch((err) => console.log(err));

        api.get("http://127.0.0.1:8000/ports")
            .then((res) => {
                console.log("PORTS:", res.data);
                setPorts(res.data);
            })
            .catch((err) => console.log(err));

        api.get("http://127.0.0.1:8000/file_hashes")
            .then((res) => {
                console.log("FILES:", res.data);
                setFiles(res.data);
            })
            .catch((err) => console.log(err));

        api.get("http://127.0.0.1:8000/hosts")
            .then((res) => {
                console.log("HOSTS:", res.data);
                setHosts(res.data);
            })
            .catch((err) => console.log(err));

    }, []);

    return (
        <div>
            <h1>EDR Dashboard</h1>

            {/* TELEMETRY */}
            <h2>Telemetry</h2>
            {telemetry.map(t => (
                <div key={t.id}>
                    <p>{t.hostname}</p>
                    <p>CPU: {t.cpu_percent}%</p>
                    <p>RAM: {t.memory_percent}%</p>
                    <p>Disk: {t.disk_percent}%</p>
                    <hr />
                </div>
            ))}

            {/* PROCESSES */}
            <h2>Processes</h2>
            {processes.map(p => (
                <div key={p.id}>
                    <p>{p.process_name}</p>
                    <p>CPU: {p.cpu_percent}%</p>
                    <p>MEM: {p.memory_percent}%</p>
                    <hr />
                </div>
            ))}

            {/* ALERTS */}
            <h2>Alerts</h2>
            {alerts.map(a => (
                <div key={a.id}>
                    <p>{a.alert_type}</p>
                    <p>{a.message}</p>
                    <p>{a.severity}</p>
                    <hr />
                </div>
            ))}

            {/* PORTS */}
            <h2>Ports</h2>
            {ports.map(p => (
                <div key={p.id}>
                    <p>Port: {p.port}</p>
                    <p>PID: {p.pid ?? "N/A"}</p>
                    <hr />
                </div>
            ))}

            {/* FILE HASHES */}
            <h2>File Hashes</h2>
            {files.map(f => (
                <div key={f.id}>
                    <p>{f.file_path}</p>
                    <p>{f.hash_value}</p>
                    <hr />
                </div>
            ))}

            {/* HOSTS */}
            <h2>Hosts</h2>
            {hosts.map((h, i) => (
                <div key={i}>
                    <p>{h}</p>
                    <hr />
                </div>
            ))}
        </div>
    );
}

export default Dashboard;