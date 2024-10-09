# Commands Reference

`pan-scm-sdk` provides several commands to facilitate the cloning of configurations between SCM tenants.

## Global Options

- `--help`: Show the help message and exit.

## Commands

### create-secrets-file

Generate a `.secrets.yaml` file to securely store your SCM credentials.

**Usage:**

<div class="termy">

<!-- termynal -->
```bash
$ scm-clone create-secrets-file [OPTIONS]
```
</div>

**Options:**

- `--output-file`, `-o`: Path where the secrets YAML file will be saved (default: `.secrets.yaml`).

### clone-address-objects

Clone address objects from the source SCM tenant to the destination tenant.

**Usage:**

<div class="termy">

<!-- termynal -->
```bash
$ scm-clone clone-address-objects [OPTIONS]
```
</div>

**Options:**

- `--settings-file`, `-s`: Path to the YAML file containing SCM credentials (default: `.secrets.yaml`).

### clone-address-groups

Clone address groups from the source SCM tenant to the destination tenant.

**Usage:**

<div class="termy">

<!-- termynal -->
```bash
$ scm-clone clone-address-groups [OPTIONS]
```
</div>

**Options:**

- `--settings-file`, `-s`: Path to the YAML file containing SCM credentials (default: `.secrets.yaml`).

---

For detailed examples and use cases, see the [Examples](examples.md) section.
