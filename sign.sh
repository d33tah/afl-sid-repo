#!/bin/bash
find -name '*Release' | xargs -I'{}' -n1 sh -c "gpg --sign -b -a --default-key 69558B29995C946F -o {}.gpg {}"
