#include <seccomp.h>
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>

int main() {
	// SCMP_ACT_ALLOW: Permissive mode, but traps specific lethal calls
	scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_ALLOW);
	
	// KILL process on these attempts:
	seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(ptrace), 0);      // Anti-Debugging
	seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(mount), 0);       // Anti-Filesystem Escape
	seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(umount2), 0);
	seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(kexec_load), 0);  // Anti-Kernel Patching
	seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(reboot), 0);
	seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(init_module), 0); // Anti-Driver Loading
	seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(finit_module), 0);
	
	int fd = open("seccomp.bpf", O_WRONLY | O_CREAT | O_TRUNC, 0644);
	if (fd >= 0) {
		seccomp_export_bpf(ctx, fd);
		close(fd);
	}
	seccomp_release(ctx);
	return 0;
}
