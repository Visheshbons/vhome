// ---------- Imports ---------- \\

// Miscellaneous imports
import chalk from 'chalk';

// Imports for connecting to python clients
import { WebSocketServer } from "ws";
import os from "os";
import { fileURLToPath } from "url";
import { dirname, extname } from "path";



// ---------- Initialisation ---------- \\

const PORT = 8080;
const HOST = "0.0.0.0";
const wss = new WebSocketServer({ port: PORT, host: HOST });

let speakers = [];
let cameras = [];
let lights = [];
let devices = [];

class Device {
    constructor(type, ws) {
        this.type = type;
        this.id = id;
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

wss.on('connection', (ws, req) => {
    console.log(`New connection from ${req.socket.remoteAddress}`);

    ws.on('message', (msg) => {
        try {
            const data = JSON.parse(msg);
            if (data.type === "register") {
                new Device(data.deviceType, ws);
                console.log(`
                    Registered new 
                    ${chalk.grey(data.deviceType)}: 
                    [${chalk.green(
                        devices[devices.length - 1].id
                    )}]
                `);
            }
        } catch (err) {
            console.error('Error parsing message:', err);
        }
    });
    
    ws.on('close', () => {
        console.log(`Connection closed from ${req.socket.remoteAddress}`);
    });
})



// ---------- Start Server ---------- \\

wss.on('listening', () => {
    console.log(`WebSocket server running on port ${chalk.green(PORT)}`);
    console.log(`Network at "ws://${getServerIpAddress()}:${PORT}"\n`);
})