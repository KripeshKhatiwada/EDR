import { useEffect, useState } from "react";
import api from "../services/api";
import "./dashboard.css";

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

        <h1>
            EDR SECURITY DASHBOARD
        </h1>

      <div className="grid">

            {/* TELEMETRY */}
            <div className="card">
                <h2 >Telemetry</h2>
                {telemetry.map(t => (
                    <div key={t.id} className="item">
                        <b>{t.hostname}</b>
                        <br />
                        CPU: {t.cpu_percent}% | RAM: {t.memory_percent}% | DISK: {t.disk_percent}%
                    </div>
                ))}
            </div>

            {/* ALERTS */}
            <div className="card">
                <h2 >Alerts</h2>
                {alerts.map(a => (
                    <div key={a.id} className="item alert">
                        <b>{a.alert_type}</b>
                        <br />
                        {a.message}
                        <br />
                        <span>{a.severity}</span>
                    </div>
                ))}
            </div>

            {/* PROCESSES */}
            <div className="card">
                <h2 >Processes</h2>
                {processes.map(p => (
                    <div key={p.id} className="item">
                        {p.process_name}
                        <br />
                        CPU: {p.cpu_percent}% | MEM: {p.memory_percent}%
                    </div>
                ))}
            </div>

            {/* PORTS */}
            <div className="card">
                <h2 >Ports</h2>
                {ports.map(p => (
                    <div key={p.id} className="item">
                        Port: {p.port} | PID: {p.pid ?? "N/A"}
                    </div>
                ))}
            </div>

            {/* FILE HASHES */}
            <div className="card">
                <h2 >File Hashes</h2>
                {files.map(f => (
                    <div key={f.id} className="item">
                        <b>{f.file_path}</b>
                        <br />
                        <span className="small">{f.hash_value}</span>
                    </div>
                ))}
            </div>

            {/* HOSTS */}
            <div className="card">
                <h2 >Hosts</h2>
                {hosts.map((h, i) => (
                    <div key={i} className="item">
                        {h}
                    </div>
                ))}
            </div>

        </div>
    </div>
    );
}

export default Dashboard;