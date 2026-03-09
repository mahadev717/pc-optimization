using System;
using System.Diagnostics;
using System.Net;
using System.Net.Sockets;
using System.Security.Principal;
using System.Windows.Forms;

namespace HackerLauncher
{
    class Program
    {
        static void Main(string[] args)
        {
            if (!IsAdministrator())
            {
                var processInfo = new ProcessStartInfo(Application.ExecutablePath);
                processInfo.Verb = "runas";
                try
                {
                    Process.Start(processInfo);
                }
                catch (Exception)
                {
                    MessageBox.Show("Administrator privileges are required.", "Access Denied", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
                Application.Exit();
            }
            else
            {
                LaunchSystem();
            }
        }

        static bool IsAdministrator()
        {
            var identity = WindowsIdentity.GetCurrent();
            var principal = new WindowsPrincipal(identity);
            return principal.IsInRole(WindowsBuiltInRole.Administrator);
        }

        static void KillOldServers()
        {
            // Kill any python processes listening on port 5050
            try
            {
                var killProc = new Process();
                killProc.StartInfo.FileName = "cmd.exe";
                killProc.StartInfo.Arguments = "/c \"for /f \"tokens=5\" %a in ('netstat -ano ^| findstr :5050.*LISTENING') do taskkill /F /PID %a\"";
                killProc.StartInfo.CreateNoWindow = true;
                killProc.StartInfo.UseShellExecute = false;
                killProc.Start();
                killProc.WaitForExit(5000);
            }
            catch (Exception) { }
        }

        static void LaunchSystem()
        {
            string currentDir = AppDomain.CurrentDomain.BaseDirectory;

            // Kill old server processes first
            KillOldServers();
            System.Threading.Thread.Sleep(1000);

            // Start Python Server hidden (no console window)
            Process serverProcess = new Process();
            serverProcess.StartInfo.FileName = "python.exe";
            serverProcess.StartInfo.Arguments = "server.py";
            serverProcess.StartInfo.WorkingDirectory = currentDir;
            serverProcess.StartInfo.CreateNoWindow = true;
            serverProcess.StartInfo.UseShellExecute = false;
            serverProcess.StartInfo.WindowStyle = ProcessWindowStyle.Hidden;

            try
            {
                serverProcess.Start();
                System.Threading.Thread.Sleep(2500);
                Process.Start(new ProcessStartInfo("http://127.0.0.1:5050") { UseShellExecute = true });
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error starting system: " + ex.Message, "System Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }
}
