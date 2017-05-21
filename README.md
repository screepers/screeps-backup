# screeps-backup

This is a backup and restore utility for the [Screeps](https://screeps.com/)
game world. It backs up both memory and segment data.


## Configuration

This project uses the same style config as the Screeps [Console](https://github.com/screepers/screeps_console),
[Notify](https://github.com/screepers/screeps_notify) and [Stats](https://github.com/screepers/screeps-stats)
projects. If you have them configured you are all set to go.

Settings for just this utility can also be created by copying the
`.screeps_settings.dist.yaml` to `.screeps_settings.yaml` and filling it out.


## Setup

The simpliest way to get this working is by using `make`.


## Running

To backup files run `screeps_backup /path/to/backups`.

To restore run `screeps_restore /path/to/backups/specific_backup`.

