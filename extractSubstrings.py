
row = '2018-02-22 13:01:17,298 ERROR org.dspace.ctask.fixity.CheckFixity @ Unable to retreive bitstream in item: 1774.2/45533 . Bitstream: \'1948_53_11.pdf\' (seqId: 1) error: /mnt/dspace/storage/assetstore/15/11/07/151107968919162447768858185989272549890 (No such file or directory)'

print row[row.index('1774.2/'):row.index(' . Bitstream:')]
