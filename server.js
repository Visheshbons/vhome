// ---------- Imports ---------- \\

// Miscellaneous imports
import chalk from 'chalk';

// Imports for connecting to python clients
import { WebSocketServer } from "ws";
import os from "os";
import { fileURLToPath } from "url";
import { dirname, extname } from "path";



// ---------- Initialisation ---------- \\

const PORT = 5000;
const HOST = "0.0.0.0";

let speakers = [];
let cameras = [];
let lights = [];
let devices = [];

class Device {
    constructor(type, ws) {
        this.type = type;
        this.ws = ws;

        switch (type) {
            case "speaker":
                speakers.push(this);
                devices.push(this);
                this.id = `SPK-${speakers.length.toString().padStart(3, '0')}`;
                break;
            case "camera":
                cameras.push(this);
                devices.push(this);
                this.id = `CAM-${cameras.length.toString().padStart(3, '0')}`;
                break;
            case "light":
                lights.push(this);
                devices.push(this);
                this.id = `LGT-${lights.length.toString().padStart(3, '0')}`;
                break;
            default:
                this.id = `DEV-000`;
        }
    }
}

// ---------- Helper Functions ---------- \\

function getServerIpAddress() {
  const networkInterfaces = os.networkInterfaces();
  let ipAddress = "N/A";

  for (const interfaceName in networkInterfaces) {
    const networkInterface = networkInterfaces[interfaceName];
    for (const addressInfo of networkInterface) {
      // Filter for IPv4 addresses that are not internal (loopback)
      if (addressInfo.family === "IPv4" && !addressInfo.internal) {
        ipAddress = addressInfo.address;
        return ipAddress; // Return the first non-internal IPv4 address found
      }
    }
  }
  return ipAddress;
}

// Legacy ID creation
// function createId(type) {
//     switch(type) {
//         case "speaker":
//             speakerCount++;
//             return `SPK-${speakerCount}`;
//         case "camera":
//             cameraCount++;
//             return `CAM-${cameraCount}`;
//         case "light":
//             lightCount++;
//             return `LGT-${lightCount}`;
//         default:
//             return `DEV-000`;
//     }
// }



// ---------- Server Routes ---------- \\

function setupServerEvents(wss) {
    wss.on('connection', (ws, req) => {
        console.log(`New connection from ${req.socket.remoteAddress}`);

        ws.on('message', (msg) => {
            try {
                const data = JSON.parse(msg);
                if (data.type === "register") {
                    new Device(data.deviceType, ws);
                    console.log(`Registered new ${
                        chalk.grey(data.deviceType)
                    }: [${
                        chalk.green(devices[devices.length - 1].id)
                    }]`);
                    ws.send(
                        JSON.stringify({ 
                            type: "registered", 
                            Id: devices[devices.length - 1].id 
                        })
                    );
                }
            } catch (err) {
                console.error('Error parsing message:', err);
            }
        });

        ws.on('close', () => {
            try {
                const deviceIndex = devices.findIndex(d => d.ws === ws);

                if (deviceIndex !== -1) {
                    const device = devices[deviceIndex];
                    const type = device.type;

                    switch (type) {
                        case "speaker": speakers = speakers.filter(dev => dev.ws !== ws); break;
                        case "camera": cameras = cameras.filter(dev => dev.ws !== ws); break;
                        case "light": lights = lights.filter(dev => dev.ws !== ws); break;
                    }

                    devices = devices.filter(dev => dev.ws !== ws);

                    console.log(`Disconnected ${chalk.grey(type)}: [${chalk.red(device.id)}]`);
                } else {
                    console.log(`An unknown client disconnected from ${req.socket.remoteAddress}`);
                }
            } catch (err) {
                console.error(`Error handling disconnection: ${chalk.red(err)}`);
            }
        });
    });
}



// ---------- Start Server ---------- \\

function startWebSocketServer(port) {
    return new Promise((resolve, reject) => {
        const server = new WebSocketServer({ port, host: HOST });

        server.on("listening", () => {
            resolve({ server, port });
        });

        server.on("error", (err) => {
            if (err.code === "EADDRINUSE") {
                console.log(chalk.yellow(`Port ${port} is in use, retrying on ${port + 1}...`));
                resolve(startWebSocketServer(port + 1)); // recursive retry
            } else {
                reject(err);
            }
        });
    });
}

let wss;  // must be declared but NOT assigned

startWebSocketServer(PORT).then(({ server, port }) => {
    wss = server;

    console.log(`WebSocket server running on port ${chalk.green(port)}`);
    console.log(`Network at "ws://${getServerIpAddress()}:${port}"\n`);

    setupServerEvents(wss);

}).catch(err => {
    console.error("Failed to start WebSocket server:", err);
});