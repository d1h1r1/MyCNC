const fs = require('fs');

// 假设 CNC 机器的最大加速度（mm/s²）
const ACCELERATION = 500; // 可根据 CNC 机器调整
const maxSpeed = 2500

function parseGCode(filePath) {
    const data = fs.readFileSync(filePath, 'utf-8');
    const lines = data.split('\n');

    let commands = [];
    let x = 0, y = 0, z = 0, f = 2500; // 初始位置和默认进给速度

    lines.forEach(line => {
        line = line.trim();
        if (line.startsWith('G0') || line.startsWith('G1') || line.startsWith('G2') || line.startsWith('G3')) {
            let newX = line.match(/X([\d\.\-]+)/);
            let newY = line.match(/Y([\d\.\-]+)/);
            let newZ = line.match(/Z([\d\.\-]+)/);
            let newF = line.match(/F([\d\.\-]+)/);
            let i = line.match(/I([\d\.\-]+)/);
            let j = line.match(/J([\d\.\-]+)/);

            newX = newX ? parseFloat(newX[1]) : x;
            newY = newY ? parseFloat(newY[1]) : y;
            newZ = newZ ? parseFloat(newZ[1]) : z;

            if (line.startsWith('G0')) {
                newF = maxSpeed;
            } else {
                newF = newF ? parseFloat(newF[1]) : f;
            }

            let dist = 0;
            if (line.startsWith('G1') || line.startsWith('G0')) {
                // 直线长度计算
                dist = Math.sqrt((newX - x) ** 2 + (newY - y) ** 2 + (newZ - z) ** 2);
            } else if (line.startsWith('G2') || line.startsWith('G3')) {
                // 圆弧长度计算
                if (i && j) {
                    let centerX = x + parseFloat(i[1]);
                    let centerY = y + parseFloat(j[1]);
                    let radius = Math.sqrt((x - centerX) ** 2 + (y - centerY) ** 2);
                    let theta = Math.atan2(newY - centerY, newX - centerX) - Math.atan2(y - centerY, x - centerX);

                    if (line.startsWith('G2') && theta < 0) {
                        theta += 2 * Math.PI;
                    }
                    if (line.startsWith('G3') && theta > 0) {
                        theta -= 2 * Math.PI;
                    }

                    let arcLength = Math.abs(theta) * radius;
                    dist = arcLength;
                }
            }

            commands.push({ line, dist, feed: newF });
            x = newX;
            y = newY;
            z = newZ;
            f = newF;
        }
    });

    return commands;
}

function calculateTimeWithAcceleration(commands) {
    let totalTime = 0;

    commands.forEach(({ dist, feed }) => {
        if (feed > 0) {
            let F_mm_s = feed / 60.0;

            let tAcc = F_mm_s / ACCELERATION; // 加速时间
            let dAcc = 0.5 * ACCELERATION * (tAcc ** 2); // 加速段的位移
            let dDec = dAcc; // 减速段位移相同
            let tDec = tAcc; // 减速时间相同

            if (dist >= (dAcc + dDec)) {
                let dUniform = dist - (dAcc + dDec);
                let tUniform = dUniform / F_mm_s;
                totalTime += (tAcc + tUniform + tDec);
            } else {
                let tTotal = Math.sqrt(2 * dist / ACCELERATION);
                totalTime += tTotal;
            }
        }
    });

    return formatTime(totalTime);
}

function formatTime(seconds) {
    let hours = Math.floor(seconds / 3600);
    let minutes = Math.floor((seconds % 3600) / 60);
    let secs = Math.floor(seconds % 60);
    return `${hours} 小时 ${minutes} 分钟 ${secs} 秒`;
}

// 示例调用
const gcodeFile = '3.8use.nc';
const commands = parseGCode(gcodeFile);
const processingTime = calculateTimeWithAcceleration(commands);

console.log(`预计加工时间（考虑加速度）: ${processingTime}`);
