#!/usr/bin/env python

import sys
from lib.ngram_frequency_index import Cconstrastive_analyser

if __name__ == '__main__':
  if len(sys.argv) == 1:
    print>>sys.stderr,'Usage:',sys.argv[0],' folder_with_indexes'
    sys.exit(0)

analyser = Cconstrastive_analyser(sys.argv[1])
analyser.run()
