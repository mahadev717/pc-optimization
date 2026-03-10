using System;
using System.Diagnostics;
using System.Drawing;
using System.Net.Sockets;
using System.Security.Principal;
using System.Windows.Forms;
using System.Threading;

namespace HackerLauncher
{
    // ═══════════════════════════════════════════════════════════════════════════
    // Main launch window
    // ═══════════════════════════════════════════════════════════════════════════
    class LaunchForm : Form
    {
        private bool _serverStarted = false;

        public LaunchForm()
        {
            this.Text            = "NEURAL LINK v6.0";
            this.Size            = new Size(480, 290);
            this.StartPosition   = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.MaximizeBox     = false;
            this.BackColor       = Color.FromArgb(6, 10, 14);
            this.ForeColor       = Color.FromArgb(0, 243, 255);
            this.Font            = new Font("Consolas", 9f, FontStyle.Regular);

            var title = new Label
            {
                Text      = "HACKER CONTROL CENTER",
                ForeColor = Color.FromArgb(0, 243, 255),
                Font      = new Font("Consolas", 14f, FontStyle.Bold),
                AutoSize  = false,
                Size      = new Size(460, 30),
                Location  = new Point(10, 28),
                TextAlign = ContentAlignment.MiddleCenter
            };

            var sub = new Label
            {
                Text      = "NEURAL LINK v6.0  |  BLUESTACKS BEAST MODE",
                ForeColor = Color.FromArgb(255, 136, 0),
                Font      = new Font("Consolas", 7f, FontStyle.Regular),
                AutoSize  = false,
                Size      = new Size(460, 20),
                Location  = new Point(10, 60),
                TextAlign = ContentAlignment.MiddleCenter
            };

            var divider = new Label
            {
                Text      = new string('\u2500', 58),
                ForeColor = Color.FromArgb(0, 80, 90),
                AutoSize  = false,
                Size      = new Size(460, 16),
                Location  = new Point(10, 84),
                TextAlign = ContentAlignment.MiddleCenter
            };

            var statusLabel = new Label
            {
                Name      = "statusLabel",
                Text      = "[ READY ] Choose an option below",
                ForeColor = Color.FromArgb(57, 255, 20),
                Font      = new Font("Consolas", 8f, FontStyle.Regular),
                AutoSize  = false,
                Size      = new Size(460, 22),
                Location  = new Point(10, 106),
                TextAlign = ContentAlignment.MiddleCenter
            };

            var btnLaunch = new Button
            {
                Text      = "\u25B6  LAUNCH OPTIMIZER",
                Size      = new Size(400, 52),
                Location  = new Point(40, 148),
                FlatStyle = FlatStyle.Flat,
                BackColor = Color.FromArgb(6, 10, 14),
                ForeColor = Color.FromArgb(0, 243, 255),
                Font      = new Font("Consolas", 9f, FontStyle.Bold),
                Cursor    = Cursors.Hand
            };
            btnLaunch.FlatAppearance.BorderColor = Color.FromArgb(0, 243, 255);
            btnLaunch.FlatAppearance.BorderSize  = 1;
            btnLaunch.MouseEnter += (s, e) => { btnLaunch.BackColor = Color.FromArgb(0, 30, 36); };
            btnLaunch.MouseLeave += (s, e) => { btnLaunch.BackColor = Color.FromArgb(6, 10, 14); };
            btnLaunch.Click += (s, e) => OnLaunchClick(statusLabel, btnLaunch);

            var divider2 = new Label
            {
                Text      = new string('\u2500', 58),
                ForeColor = Color.FromArgb(0, 80, 90),
                AutoSize  = false,
                Size      = new Size(460, 16),
                Location  = new Point(10, 218),
                TextAlign = ContentAlignment.MiddleCenter
            };

            var footer = new Label
            {
                Text      = "Antigravity  //  Free Fire 300+ FPS  //  4GB RAM Optimized",
                ForeColor = Color.FromArgb(0, 60, 70),
                Font      = new Font("Consolas", 7f, FontStyle.Regular),
                AutoSize  = false,
                Size      = new Size(460, 18),
                Location  = new Point(10, 238),
                TextAlign = ContentAlignment.MiddleCenter
            };

            this.Controls.AddRange(new Control[]
            {
                title, sub, divider, statusLabel,
                btnLaunch,
                divider2, footer
            });
        }

        // ── LAUNCH OPTIMIZER ─────────────────────────────────────────────────
        private void OnLaunchClick(Label statusLabel, Button btnLaunch)
        {
            if (_serverStarted)
            {
                SetStatus(statusLabel, "[ ONLINE ] Opening optimizer...", Color.FromArgb(57, 255, 20));
                Process.Start(new ProcessStartInfo("http://127.0.0.1:5050") { UseShellExecute = true });
                return;
            }

            btnLaunch.Enabled = false;
            SetStatus(statusLabel, "[ BOOT ] Starting server...", Color.FromArgb(255, 136, 0));

            var t = new Thread(() =>
            {
                string dir = AppDomain.CurrentDomain.BaseDirectory;
                Program.KillOldServers();
                Thread.Sleep(800);

                Invoke((Action)(() => SetStatus(statusLabel, "[ SETUP ] Installing dependencies...", Color.FromArgb(255, 136, 0))));
                Program.InstallDependencies();

                Invoke((Action)(() => SetStatus(statusLabel, "[ BOOT ] Launching Python server...", Color.FromArgb(255, 136, 0))));

                var srv = new Process();
                srv.StartInfo.FileName         = "python.exe";
                srv.StartInfo.Arguments        = "server.py";
                srv.StartInfo.WorkingDirectory = dir;
                srv.StartInfo.CreateNoWindow   = true;
                srv.StartInfo.UseShellExecute  = false;
                srv.StartInfo.WindowStyle      = ProcessWindowStyle.Hidden;

                try { srv.Start(); }
                catch (Exception ex)
                {
                    Invoke((Action)(() =>
                    {
                        MessageBox.Show("Could not start Python.\n\nMake sure Python is installed and added to PATH.\nDownload: https://python.org\n\nError: " + ex.Message,
                            "Python Not Found", MessageBoxButtons.OK, MessageBoxIcon.Error);
                        btnLaunch.Enabled = true;
                        SetStatus(statusLabel, "[ ERROR ] Python not found.", Color.FromArgb(255, 60, 60));
                    }));
                    return;
                }

                Invoke((Action)(() => SetStatus(statusLabel, "[ WAIT ] Waiting for server on port 5050...", Color.FromArgb(255, 136, 0))));

                bool ready = Program.WaitForServer(30);

                Invoke((Action)(() =>
                {
                    btnLaunch.Enabled = true;
                    if (ready)
                    {
                        _serverStarted = true;
                        SetStatus(statusLabel, "[ ONLINE ] Server ready! Browser opening...", Color.FromArgb(57, 255, 20));
                        Process.Start(new ProcessStartInfo("http://127.0.0.1:5050") { UseShellExecute = true });
                    }
                    else
                    {
                        SetStatus(statusLabel, "[ TIMEOUT ] Server did not start in 30s.", Color.FromArgb(255, 60, 60));
                        MessageBox.Show("Server did not start within 30 seconds.\n\nPossible causes:\n  - Python not installed\n  - Flask not installed\n  - Antivirus blocking server.py\n  - Port 5050 blocked by firewall",
                            "Server Startup Failed", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    }
                }));
            });
            t.IsBackground = true;
            t.Start();
        }


        private void SetStatus(Label lbl, string text, Color color)
        {
            lbl.Text      = text;
            lbl.ForeColor = color;
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Entry point + helpers
    // ═══════════════════════════════════════════════════════════════════════════
    class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            if (!IsAdministrator())
            {
                var processInfo = new ProcessStartInfo(Application.ExecutablePath);
                processInfo.Verb = "runas";
                try { Process.Start(processInfo); }
                catch { MessageBox.Show("Administrator privileges required.", "Access Denied", MessageBoxButtons.OK, MessageBoxIcon.Error); }
                Application.Exit();
                return;
            }

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new LaunchForm());
        }

        public static bool IsAdministrator()
        {
            var identity  = WindowsIdentity.GetCurrent();
            var principal = new WindowsPrincipal(identity);
            return principal.IsInRole(WindowsBuiltInRole.Administrator);
        }

        public static bool IsServerRunning()
        {
            try
            {
                using (var client = new TcpClient())
                {
                    var result   = client.BeginConnect("127.0.0.1", 5050, null, null);
                    bool success = result.AsyncWaitHandle.WaitOne(600);
                    return success && client.Connected;
                }
            }
            catch { return false; }
        }

        public static void KillOldServers()
        {
            try
            {
                var p = new Process();
                p.StartInfo.FileName  = "cmd.exe";
                p.StartInfo.Arguments = "/c \"for /f \"tokens=5\" %a in ('netstat -ano ^| findstr :5050.*LISTENING') do taskkill /F /PID %a\"";
                p.StartInfo.CreateNoWindow  = true;
                p.StartInfo.UseShellExecute = false;
                p.Start();
                p.WaitForExit(5000);
            }
            catch { }
        }

        public static void InstallDependencies()
        {
            try
            {
                var p = new Process();
                p.StartInfo.FileName  = "pip";
                p.StartInfo.Arguments = "install flask flask-cors --quiet --disable-pip-version-check";
                p.StartInfo.CreateNoWindow  = true;
                p.StartInfo.UseShellExecute = false;
                p.Start();
                p.WaitForExit(60000);
            }
            catch { }
        }

        public static bool WaitForServer(int timeoutSeconds = 30)
        {
            int attempts = timeoutSeconds * 2;
            for (int i = 0; i < attempts; i++)
            {
                Thread.Sleep(500);
                if (IsServerRunning()) return true;
            }
            return false;
        }
    }
}
