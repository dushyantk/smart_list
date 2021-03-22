"""
Implement the "lss" command in Python.

The command needs to accept one optional argument: a path to the directory or file, similar to the "ls" command.

Make it as general as possible. The goal is to find sequences of files that can be concatenated together. 
Please don't rely on specific characters as delimiters since we can't control how artists name their files. 
And don't assume anything about the zero-padding.

Note: This code is written to work with Python 3 and 2 both, so if you see the results inside parentheses you are probably running Python 2.x

"""
import argparse
import collections
import os
import re

def makenonpaddedname(match):
    """
    Function to return file names of non sequential files.

    :param object match: 
    :return: Non padded file name
    :rtype: str
    """

    prefix = match.string[:match.start()]
    suffix = match.string[match.end():]
    template = prefix + "%d" + suffix

    return match.expand(template)

def makepaddedname(match):
    """
    Function to return file names of sequential files.

    :param object match: 
    :return: Padded file name
    :rtype: str
    """

    prefix = match.string[:match.start()]
    suffix = match.string[match.end():]
    padding = "%%0%dd" % (match.end() - match.start())
    template = prefix + padding + suffix
    return match.expand(template)

def extractsequences(filename):
    """
    Extracts Sequence, priority and frame number from the file name.

    :param str filename: the file name to process
    :return: Sequence, priority and frame number .
    :rtype: iterator 
    """

    yield (filename, 2, None)
    for m in re.finditer(r"(?!0)[0-9]+", filename):
        frameno = int(m.group())
        yield (makenonpaddedname(m), 0, frameno)
    for m in re.finditer(r"[0-9]+", filename):
        frameno = int(m.group())
        if m.end() - m.start() > 1:
            yield (makepaddedname(m), 1, frameno)

def format_subrange(start, end, step):
    """
    Takes start end and step to return a formatted string.

    :param int start: the start frame
    :param int end: the end frame
    :param int step: step number
    :return: Formatted subrange.
    :rtype: str 
    """
    
    if start == end:
        return str(start)
    elif step == 1:
        return "%d-%d" % (start, end)
    else:
        return "%d-%dx%d" % (start, end, step)

class Range(object):
    """
    Detects the frame ranges as they are and reveals the reality of the broken world.
    """

    def __init__(self):
        self.frames = set()

    def add(self, frame):
        if frame is not None:
            self.frames.add(frame)

    def __str__(self):
        """
        Class object as a string, gives you frame ranges as first and last frames.

        :return: Frame range.
        :rtype: str
        """

        nframes = len(self.frames)
        if nframes == 0:
            return ""
        elif nframes == 1:
            frame, = self.frames
            return str(frame)
        else:
            frames = sorted(self.frames)
            start = prev = frames[0] # First frame.
            step = None
            subranges = []
            for end in frames[1:]: # Frame starting from the second in the list.

                if step is None: # Step is still none.
                    step = end - prev # Find and set step.

                if prev + step != end: # If the sequence is broken.
                    subranges.append((start, prev, step)) # Create a subrange.
                    step = None # Reset step.
                    start = end # Re-start start.
                prev = end # The next previous.

            else:
                subranges.append((start, end, step))

            return ", ".join(format_subrange(start, end, step) for (start, end, step) in subranges)

    def __repr__(self):
        """
        Won't return a string that describes the pointer of this object, even if you try it.
        """
        return self.__str__()

    def __bool__(self):
        return bool(self.frames)

    def __len__(self):
        return max(1, len(self.frames))

def parsefilenames(filenames):
    """
    Main parser, gathering data from rest of the code.

    ::param list[str] filenames: list of filenames
    :return: sorted list of data elements.
    :rtype: list
    """

    sequence_counts = collections.defaultdict(int)
    sequences_by_filenames = collections.defaultdict(list)

    for filename in filenames:

        for sequence, priority, frameno in extractsequences(filename):
            sequence_counts[sequence] += 1
            sequences_by_filenames[filename].append((sequence, priority, frameno))

    sequences = collections.defaultdict(Range)

    for filename, filesequences in sequences_by_filenames.items():
        (sequence, _, frameno) = max(filesequences, key=lambda s_p_f: (sequence_counts[s_p_f[0]], s_p_f[1]))
        sequences[sequence].add(frameno)
    
    return sorted(sequences.items())

def main():
    """
    Hero function, called when running the program. Contains a parser to take directory path input.

    Prints desired rusults.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("folder")
    args = parser.parse_args()
    
    print("")
    print("Smart Listing:", args.folder.replace("/", " >"))
    print("")
    for seq, frange in parsefilenames(os.listdir(args.folder)):
        print(len(frange), seq, frange)

if __name__ == "__main__":
    main()
