
# -*- coding: utf-8 -*-
import re
import sys
import os
from equant import main


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(equant-script\.pyw?|\.exe)?$', '', sys.argv[0])
    os.chdir(os.path.abspath(sys.argv[0]))
    sys.exit(main())
