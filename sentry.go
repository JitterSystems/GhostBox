package main

import (
	"fmt"
	"os"
	"os/exec"
	"runtime"
	"syscall"
)

// The Sentry: NSA/CIA-Grade Policy Engine
func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: ./sentry <command> [args...]")
		os.Exit(1)
	}
	
	runtime.LockOSThread()
	
	cmd := exec.Command(os.Args[1], os.Args[2:]...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.SysProcAttr = &syscall.SysProcAttr{Ptrace: true}
	
	if err := cmd.Start(); err != nil {
		os.Exit(1)
	}
	
	cmd.Wait() // Initial trap
	
	var regs syscall.PtraceRegs
	for {
		// Stop BEFORE the kernel handles the request
		if err := syscall.PtraceSyscall(cmd.Process.Pid, 0); err != nil {
			break
		}
		if err := cmd.Wait(); err != nil {
			break
		}
		if err := syscall.PtraceGetRegs(cmd.Process.Pid, &regs); err != nil {
			break
		}
		
		syscallNum := regs.Orig_rax
		
		// --- THE GHOST POLICY: HIDE & BLOCK ---
		
		switch syscallNum {
			
			// 1. ANTI-FORENSICS: Block hardware/ID discovery
			case syscall.SYS_UNAME, syscall.SYS_SYSINFO:
				// Policy: Spoof the Kernel version to an outdated/generic one
				// This confuses automated exploit kits and fingerprinting tools.
				fmt.Println("[Sentry] POLICY: Spoofing System Identity.")
				regs.Orig_rax = syscall.SYS_GETPID // Divert to a harmless call
				syscall.PtraceSetRegs(cmd.Process.Pid, &regs)
				
				// 2. PRIVILEGE ESCAPE BLOCK: No New Namespaces
			case syscall.SYS_UNSHARE, syscall.SYS_CLONE:
				// Prevent the app from creating its own "nested" sandbox to hide from us.
				fmt.Println("[Sentry] POLICY: Blocking Nested Isolation.")
				regs.Orig_rax = 0xffffffffffffffff 
				syscall.PtraceSetRegs(cmd.Process.Pid, &regs)
				
				// 3. DATA EXFILTRATION BLOCK: Socket Lockdown
			case syscall.SYS_LISTEN, syscall.SYS_ACCEPT:
				// Policy: The app can talk out, but NO ONE can talk in.
				fmt.Println("[Sentry] POLICY: Blocking Inbound Ghost-Connections.")
				regs.Orig_rax = 0xffffffffffffffff
				syscall.PtraceSetRegs(cmd.Process.Pid, &regs)
				
				// 4. MEMORY INTEGRITY: Block Ptrace (Self-Defense)
			case syscall.SYS_PTRACE:
				// If the app tries to ptrace itself or others to bypass the Sentry.
				fmt.Println("[Sentry] POLICY: Terminating Anti-Sentry Attempt.")
				syscall.Kill(cmd.Process.Pid, syscall.SIGKILL)
				
				// 5. THE "NSA BLOCKER": Kernel Module & Keyring access
			case syscall.SYS_INIT_MODULE, syscall.SYS_ADD_KEY, syscall.SYS_KEYCTL:
				fmt.Println("[Sentry] POLICY: High-Level Security Breach Attempt Blocked.")
				regs.Orig_rax = 0xffffffffffffffff
				syscall.PtraceSetRegs(cmd.Process.Pid, &regs)
		}
	}
}
