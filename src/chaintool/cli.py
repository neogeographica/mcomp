# -*- coding: utf-8 -*-
#
# Copyright 2021 Joel Baxter
#
# This file is part of chaintool.
#
# chaintool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# chaintool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with chaintool.  If not, see <https://www.gnu.org/licenses/>.


"""Parse command-line args and invoke the requested operation."""


__all__ = ['main']


import argparse
import os
import sys

from colorama import Fore

from . import command
from . import completions_setup
from . import sequence
from . import shortcuts_setup
from . import xfer


class SubparsersHelpAction(argparse.Action):
    # Pylint doesn't like the "help" argument in  __init__, but that's what we
    # get from argparse.
    # pylint: disable=redefined-builtin

    def __init__(self, option_strings, dest, help=None, subparsers=None):
        if subparsers is None:
            self.subparsers = []
        else:
            self.subparsers = subparsers
        super().__init__(
            option_strings=option_strings,
            dest=argparse.SUPPRESS,
            default=argparse.SUPPRESS,
            nargs=0,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        cut_prefix = os.path.basename(sys.argv[0]) + ' '
        print()
        for subp in self.subparsers:
            desc = subp.prog
            if desc.startswith(cut_prefix):
                desc = desc[len(cut_prefix):]
            print(Fore.MAGENTA + "* '{}' help:".format(desc) + Fore.RESET)
            print()
            subp.print_help()
            print()
        parser.exit()


def set_cmd_options(group_subparsers):
    group_parser_cmd = group_subparsers.add_parser(
        "cmd",
        add_help=False,
        help="Work with saved commandlines.",
        description="Work with saved commandlines.")
    cmd_subparsers = group_parser_cmd.add_subparsers(
        title="operations",
        dest="operation",
        required=True)
    cmd_parser_list = cmd_subparsers.add_parser(
        "list",
        help="List current commandline names.",
        description="List current commandline names.")
    cmd_parser_list.add_argument(
        "-c", "--column",
        action="store_true",
        help="Single-column format.")
    cmd_parser_set = cmd_subparsers.add_parser(
        "set",
        help="Create or update a named commandline.",
        description="Create or update a named commandline.")
    cmd_parser_set.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Don't display info about the resulting commandline.")
    cmd_parser_set.add_argument(
        "cmdname")
    cmd_parser_set.add_argument(
        "cmdline",
        help="Entire commandline as one argument (will probably need to be "
        "quoted). This string may include named placeholders in Python style, "
        "e.g. {placeholdername}. Such a placeholder may also include a default "
        "value string e.g. {placeholdername=2}. 'Toggle' style placeholders "
        "can also be specified, of the form {defval:+togglename:newval}. That "
        "example defines a location that will normally be the string 'defval' "
        "but can be toggled to be 'newval' instead.")
    cmd_parser_edit = cmd_subparsers.add_parser(
        "edit",
        help="Interactively edit a new or existing commandline.",
        description="Interactively edit a new or existing commandline.")
    cmd_parser_edit.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Don't display info about the resulting commandline.")
    cmd_parser_edit.add_argument(
        "cmdname")
    cmd_parser_print = cmd_subparsers.add_parser(
        "print",
        help="Display a commandline and its placeholders/defaults.",
        description="Display a commandline and its placeholders/defaults.")
    cmd_parser_print.add_argument(
        "--dump-placeholders",
        choices=["run", "vals"],
        dest="dump_placeholders",
        help=argparse.SUPPRESS)
    cmd_parser_print.add_argument(
        "cmdname")
    cmd_parser_del = cmd_subparsers.add_parser(
        "del",
        help="Delete one or more commandlines.",
        description="Delete one or more commandlines.")
    cmd_parser_del.add_argument(
        "-f", "--force",
        action="store_true",
        help="Allow deletion of commandlines currently used by sequences.")
    cmd_parser_del.add_argument(
        "cmdnames",
        nargs='+',
        metavar="cmdname",
        help="Commandline to delete. Requires that this commandline currently NOT "
        "be used by any sequence, unless the optional --force argument is specified.")
    cmd_parser_run = cmd_subparsers.add_parser(
        "run",
        help="Execute a commandline, optionally setting values for placeholders.",
        description="Execute a commandline, optionally setting values for placeholders.")
    cmd_parser_run.add_argument(
        "cmdname")
    cmd_parser_run.add_argument(
        "placeholder_args",
        nargs='*',
        metavar="placeholder_arg",
        help="Each of these items can either specify a value for a placeholder "
        "(overriding any default) or activate a 'toggle' style placeholder. A "
        "value for a 'normal' placeholder is specified with an argument of the "
        "form placeholdername=value, while a toggle is activated just by "
        "specifying +togglename.")
    cmd_parser_vals = cmd_subparsers.add_parser(
        "vals",
        help="Set/clear values for placeholders in an existing commandline.",
        description="Set/clear values for placeholders in an existing commandline.")
    cmd_parser_vals.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Don't display info about the resulting commandline.")
    cmd_parser_vals.add_argument(
        "cmdname")
    cmd_parser_vals.add_argument(
        "placeholder_args",
        nargs='+',
        metavar="placeholder_arg",
        help="Each of these items updates an existing placeholder specification "
        "in the commandline. An argument of the form placeholdername=value will "
        "set the default value for the given placeholder, while an argument of "
        "the form placeholdername will clear the default value. An argument of "
        "the form defval:+togglename:newval will replace the values for a "
        "'toggle' style placeholder.")
    group_parser_cmd.add_argument(
        "-h", "--help",
        action=SubparsersHelpAction,
        help='show detailed operations help message and exit',
        subparsers=[
            cmd_parser_list,
            cmd_parser_set,
            cmd_parser_edit,
            cmd_parser_print,
            cmd_parser_del,
            cmd_parser_run,
            cmd_parser_vals])
    return group_parser_cmd


def set_seq_options(group_subparsers):
    group_parser_seq = group_subparsers.add_parser(
        "seq",
        add_help=False,
        help="Work with sequences of saved commandlines.",
        description="Work with sequences of saved commandlines.")
    seq_subparsers = group_parser_seq.add_subparsers(
        title="operations",
        dest="operation",
        required=True)
    seq_parser_list = seq_subparsers.add_parser(
        "list",
        help="List current sequence names.",
        description="List current sequence names.")
    seq_parser_list.add_argument(
        "-c", "--column",
        action="store_true",
        help="Single-column format.")
    seq_parser_set = seq_subparsers.add_parser(
        "set",
        help="Create or update a named sequence.",
        description="Create or update a named sequence.")
    seq_parser_set.add_argument(
        "-f", "--force",
        action="store_true",
        help="Allow use of commandline names that are not currently defined.")
    seq_parser_set.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Don't display info about the resulting sequence.")
    seq_parser_set.add_argument(
        "seqname")
    seq_parser_set.add_argument(
        "cmdnames",
        nargs='+',
        metavar="cmdname",
        help="Commandline to use in this sequence. Must currently exist, unless "
        "the optional --force argument is specified. When the sequence is run, "
        "the commandlines will be run in the specified order.")
    seq_parser_edit = seq_subparsers.add_parser(
        "edit",
        help="Interactively edit a new or existing sequence.",
        description="Interactively edit a new or existing sequence.")
    seq_parser_edit.add_argument(
        "-f", "--force",
        action="store_true",
        help="Allow use of commandline names that are not currently defined.")
    seq_parser_edit.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Don't display info about the resulting sequence.")
    seq_parser_edit.add_argument(
        "seqname")
    seq_parser_print = seq_subparsers.add_parser(
        "print",
        help="Display the commandlines for the named sequence, with their "
        "available placeholders.",
        description="Display the commandlines for the named sequence, with their "
        "available placeholders.")
    seq_parser_print.add_argument(
        "--dump-placeholders",
        choices=["run", "vals"],
        dest="dump_placeholders",
        help=argparse.SUPPRESS)
    seq_parser_print.add_argument(
        "seqname")
    seq_parser_del = seq_subparsers.add_parser(
        "del",
        help="Delete one or more sequences.",
        description="Delete one or more sequences.")
    seq_parser_del.add_argument(
        "seqnames",
        nargs='+',
        metavar="seqname",
        help="Sequence to delete.")
    seq_parser_run = seq_subparsers.add_parser(
        "run",
        help="Execute a sequence, optionally setting values for commandlines' "
        "placeholders.",
        description="Execute a sequence, optionally setting values for commandlines' "
        "placeholders.")
    seq_parser_run.add_argument(
        "-i", "--ignore-errors",
        action="store_true",
        dest="ignore_errors",
        help="Continue running the sequence even if a commandline does not exist "
        "or returns an error status.")
    seq_parser_run.add_argument(
        "-s", "--skip",
        action="append",
        metavar="cmdname",
        dest="skip_cmdnames",
        help="Skip running a command, if it is in this sequence. Multiple --skip "
        "usages are allowed, to skip multiple commands.")
    seq_parser_run.add_argument(
        "seqname")
    seq_parser_run.add_argument(
        "placeholder_args",
        nargs='*',
        metavar="placeholder_arg",
        help="Each of these items must be in the same format as used for "
        "'cmd run', and they will be passed along to each commandline in this "
        "sequence when running it. It is OK if a placeholder specified here is "
        "only relevant for some subset of the commandlines.")
    seq_parser_vals = seq_subparsers.add_parser(
        "vals",
        help="Set/clear values for placeholders in a sequence's commandlines.",
        description="Set/clear values for placeholders in a sequence's commandlines.")
    seq_parser_vals.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Don't display info about the resulting sequence.")
    seq_parser_vals.add_argument(
        "seqname")
    seq_parser_vals.add_argument(
        "placeholder_args",
        nargs='+',
        metavar="placeholder_arg",
        help="Each of these items must be in the same format as used for "
        "'cmd vals', and they will be passed along to each commandline in this "
        "sequence. It is OK if a placeholder specified here is only relevant for "
        "some subset of the commandlines.")
    group_parser_seq.add_argument(
        "-h", "--help",
        action=SubparsersHelpAction,
        help='show detailed operations help message and exit',
        subparsers=[
            seq_parser_list,
            seq_parser_set,
            seq_parser_edit,
            seq_parser_print,
            seq_parser_del,
            seq_parser_run,
            seq_parser_vals])
    return group_parser_seq


def set_print_options(group_subparsers):
    group_parser_print = group_subparsers.add_parser(
        "print",
        help="Display placeholders across all commandlines.",
        description="Display placeholders across all commandlines.")
    group_parser_print.add_argument(
        "--dump-placeholders",
        choices=["run", "vals"],
        dest="dump_placeholders",
        help=argparse.SUPPRESS)
    return group_parser_print


def set_vals_options(group_subparsers):
    group_parser_vals = group_subparsers.add_parser(
        "vals",
        help="Update placeholder values across all commandlines.",
        description="Update placeholder values across all commandlines.")
    group_parser_vals.add_argument(
        "placeholder_args",
        nargs='+',
        metavar="placeholder_arg",
        help="Each of these items must be in the same format as used for "
        "'cmd vals', and they will be passed along to each commandline. It is "
        "OK if a placeholder specified here is only relevant for some subset "
        "of the commandlines.")
    return group_parser_vals


def set_export_options(group_subparsers):
    group_parser_export = group_subparsers.add_parser(
        "export",
        help="Store commandline and sequence definitions to a flat file.",
        description="Store commandline and sequence definitions to a flat file.")
    group_parser_export.add_argument(
        "file",
        metavar="outfile")
    return group_parser_export


def set_import_options(group_subparsers):
    group_parser_import = group_subparsers.add_parser(
        "import",
        help="Load commandline and sequence definitions from a flat file.",
        description="Load commandline and sequence definitions from a flat file.")
    group_parser_import.add_argument(
        "-o", "--overwrite",
        action="store_true",
        help="Allow overwriting an existing commandline/sequence with an imported "
        "definition. If this is not specified, any such conflicts will be skipped.")
    group_parser_import.add_argument(
        "file",
        metavar="infile")
    return group_parser_import


def set_extended_options(group_subparsers):
    group_parser_extended = group_subparsers.add_parser(
        "x",
        help="Configure extended functionality (shortcut commands and bash completions).",
        description="Configure extended functionality (shortcut commands and bash completions).")
    group_parser_extended.add_argument(
        "functionality",
        choices=["shortcuts", "completions"],
        help="Functionality to enable/configure.")
    return group_parser_extended


CMD_DISPATCH = {
    "list": lambda args: command.cli_list(
        args.column
    ),
    "set": lambda args: command.cli_set(
        args.cmdname,
        args.cmdline,
        True,
        not args.quiet
    ),
    "edit": lambda args: command.cli_edit(
        args.cmdname,
        not args.quiet
    ),
    "print": lambda args: command.cli_print(
        args.cmdname,
        args.dump_placeholders
    ),
    "del": lambda args: command.cli_del(
        args.cmdnames,
        args.force
    ),
    "run": lambda args: command.cli_run(
        args.cmdname,
        args.placeholder_args
    ),
    "vals": lambda args: command.cli_vals(
        args.cmdname,
        args.placeholder_args,
        not args.quiet
    )
}


def handle_cmd(args):
    return CMD_DISPATCH[args.operation](args)


SEQ_DISPATCH = {
    "list": lambda args: sequence.cli_list(
        args.column
    ),
    "set": lambda args: sequence.cli_set(
        args.seqname,
        args.cmdnames,
        args.force,
        True,
        not args.quiet
    ),
    "edit": lambda args: sequence.cli_edit(
        args.seqname,
        args.force,
        not args.quiet
    ),
    "print": lambda args: sequence.cli_print(
        args.seqname,
        args.dump_placeholders
    ),
    "del": lambda args: sequence.cli_del(
        args.seqnames
    ),
    "run": lambda args: sequence.cli_run(
        args.seqname,
        args.placeholder_args,
        args.ignore_errors,
        args.skip_cmdnames
    ),
    "vals": lambda args: sequence.cli_vals(
        args.seqname,
        args.placeholder_args,
        not args.quiet
    )
}


def handle_seq(args):
    return SEQ_DISPATCH[args.operation](args)


def handle_print(args):
    return command.cli_print_all(args.dump_placeholders)


def handle_vals(args):
    return command.cli_vals_all(args.placeholder_args)


def handle_export(args):
    return xfer.cli_export(args.file)


def handle_import(args):
    return xfer.cli_import(args.file, args.overwrite)


def handle_extended(args):
    if args.functionality == "shortcuts":
        return shortcuts_setup.configure()
    return completions_setup.configure()


CMDGROUP_DISPATCH = {
    "cmd": handle_cmd,
    "seq": handle_seq,
    "print": handle_print,
    "vals": handle_vals,
    "export": handle_export,
    "import": handle_import,
    "x": handle_extended
}


def main(forced_progname=None):
    if forced_progname is not None:
        parser = argparse.ArgumentParser(
            prog=forced_progname,
            add_help=False)
    else:
        parser = argparse.ArgumentParser(
            add_help=False)
    group_subparsers = parser.add_subparsers(
        title="command groups",
        dest="commandgroup",
        required=True)
    group_parser_cmd = set_cmd_options(group_subparsers)
    group_parser_seq = set_seq_options(group_subparsers)
    group_parser_print = set_print_options(group_subparsers)
    group_parser_vals = set_vals_options(group_subparsers)
    group_parser_export = set_export_options(group_subparsers)
    group_parser_import = set_import_options(group_subparsers)
    group_parser_extended = set_extended_options(group_subparsers)
    parser.add_argument(
        "-h", "--help",
        action=SubparsersHelpAction,
        help='show detailed help message and exit',
        subparsers=[
            group_parser_cmd,
            group_parser_seq,
            group_parser_print,
            group_parser_vals,
            group_parser_export,
            group_parser_import,
            group_parser_extended])
    args = parser.parse_args()
    return CMDGROUP_DISPATCH[args.commandgroup](args)
