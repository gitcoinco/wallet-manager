# -*- coding: utf-8 -*-
"""Define the Grant subminer management command.

Copyright (C) 2020 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from grants.models import *



class Command(BaseCommand):

    help = 'reclass grants for round 7 - https://docs.google.com/spreadsheets/d/1HcM8PsMyBLPN6QNOMnVlwLo-1Y9vNVsfp-aI3IuDveE/edit#gid=460645821'


    def handle(self, *args, **options):

        data = [[ 1122 ," Infra "],
        [ 1121 ," Infra "],
        [ 1120 ," Infra "],
        [ 1119 ," dapp "],
        [ 1118 ," dapp "],
        [ 1116 ," Community "],
        [ 1115 ," Community "],
        [ 1114 ," dapp "],
        [ 1113 ," Community "],
        [ 1112 ," dapp "],
        [ 1111 ," dapp "],
        [ 1110 ," Infra "],
        [ 1109 ," Infra "],
        [ 1108 ," dapp "],
        [ 1107 ," delete "],
        [ 1106 ," dapp "],
        [ 1105 ," dapp "],
        [ 1104 ," Infra "],
        [ 1103 ," "],
        [ 1102 ," dapp "],
        [ 1101 ," Infra "],
        [ 1100 ," dapp "],
        [ 1099 ," "],
        [ 1098 ," dapp "],
        [ 1097 ," dapp "],
        [ 1096 ," dapp "],
        [ 1095 ," matic "],
        [ 1094 ," matic "],
        [ 1093 ," dapp "],
        [ 1092 ," delete "],
        [ 1091 ," Community "],
        [ 1090 ," "],
        [ 1089 ," dapp "],
        [ 1088 ," "],
        [ 1087 ," "],
        [ 1086 ," "],
        [ 1085 ," "],
        [ 1084 ," dapp "],
        [ 1083 ," dapp "],
        [ 1082 ," "],
        [ 1081 ," "],
        [ 1080 ," dapp "],
        [ 1079 ," dapp "],
        [ 1078 ," "],
        [ 1076 ," dapp "],
        [ 1075 ," "],
        [ 1074 ," "],
        [ 1073 ," "],
        [ 1072 ," "],
        [ 1071 ," "],
        [ 1070 ," Infra "],
        [ 1069 ," dapp "],
        [ 1068 ," Infra "],
        [ 1067 ," "],
        [ 1066 ," "],
        [ 1065 ," Infra "],
        [ 1064 ," Infra "],
        [ 1063 ," "],
        [ 1062 ," "],
        [ 1061 ," Infra "],
        [ 1060 ," "],
        [ 1059 ," Infra "],
        [ 1058 ," dapp "],
        [ 1057 ," Infra "],
        [ 1056 ," "],
        [ 1055 ," Infra "],
        [ 1054 ," dapp "],
        [ 1053 ," Infra "],
        [ 1052 ," "],
        [ 1051 ," dapp "],
        [ 1050 ," Infra "],
        [ 1049 ," "],
        [ 1048 ," Infra "],
        [ 1047 ," Infra "],
        [ 1045 ," "],
        [ 1044 ," "],
        [ 1043 ," dapp "],
        [ 1041 ," Infra "],
        [ 1040 ," "],
        [ 1039 ," "],
        [ 1038 ," Infra "],
        [ 1037 ," "],
        [ 1036 ," dapp "],
        [ 1035 ," "],
        [ 1034 ," "],
        [ 1033 ," "],
        [ 1032 ," "],
        [ 1031 ," "],
        [ 1030 ," Infra "],
        [ 1029 ," Infra "],
        [ 1028 ," "],
        [ 1026 ," "],
        [ 1025 ," "],
        [ 1024 ," dapp "],
        [ 1023 ," health "],
        [ 1022 ," "],
        [ 1021 ," "],
        [ 1020 ," dapp "],
        [ 1019 ," "],
        [ 1018 ," "],
        [ 1017 ," "],
        [ 1016 ," dapp "],
        [ 1015 ," "],
        [ 1014 ," dapp "],
        [ 1013 ," "],
        [ 1012 ," dapp "],
        [ 1011 ," dapp "],
        [ 1010 ," "],
        [ 1009 ," "],
        [ 1008 ," "],
        [ 1007 ," "],
        [ 1006 ," Infra "],
        [ 1005 ," Infra "],
        [ 1004 ," Infra "],
        [ 1003 ," dapp "],
        [ 1002 ," delete "],
        [ 1001 ," "],
        [ 1000 ," Community "],
        [ 999 ," "],
        [ 998 ," "],
        [ 997 ," Community "],
        [ 996 ," "],
        [ 995 ," "],
        [ 994 ," "],
        [ 993 ," "],
        [ 992 ," dapp "],
        [ 991 ," "],
        [ 990 ," dapp "],
        [ 989 ," dapp "],
        [ 988 ," "],
        [ 987 ," dapp "],
        [ 986 ," "],
        [ 985 ," "],
        [ 984 ," "],
        [ 983 ," "],
        [ 982 ," "],
        [ 981 ," dapp "],
        [ 980 ," dapp "],
        [ 979 ," "],
        [ 978 ," Infra "],
        [ 977 ," "],
        [ 976 ," delete "],
        [ 975 ," dapp "],
        [ 974 ," dapp "],
        [ 972 ," Infra "],
        [ 971 ," "],
        [ 970 ," Infra "],
        [ 969 ," "],
        [ 968 ," Infra "],
        [ 967 ," health "],
        [ 966 ," "],
        [ 965 ," dapp "],
        [ 964 ," dapp "],
        [ 963 ," Infra "],
        [ 962 ," Infra "],
        [ 961 ," Infra "],
        [ 960 ," "],
        [ 959 ," Infra "],
        [ 958 ," "],
        [ 957 ," "],
        [ 956 ," "],
        [ 955 ," Community "],
        [ 954 ," Community "],
        [ 953 ," Community "],
        [ 952 ," dapp "],
        [ 951 ," "],
        [ 950 ," "],
        [ 949 ," "],
        [ 948 ," "],
        [ 947 ," dapp "],
        [ 946 ," Infra "],
        [ 945 ," "],
        [ 944 ," "],
        [ 943 ," Infra "],
        [ 942 ," dapp "],
        [ 941 ," dapp "],
        [ 940 ," Infra "],
        [ 939 ," "],
        [ 938 ," Infra "],
        [ 937 ," change "],
        [ 936 ," dapp "],
        [ 935 ," Infra "],
        [ 934 ," Infra "],
        [ 933 ," "],
        [ 931 ," dapp "],
        [ 930 ," Infra "],
        [ 929 ," Community "],
        [ 927 ," Community "],
        [ 926 ," delete "],
        [ 925 ," Infra "],
        [ 924 ," Infra "],
        [ 923 ," Community "],
        [ 922 ," Community "],
        [ 921 ," "],
        [ 920 ," Community "],
        [ 919 ," "],
        [ 918 ," dapp "],
        [ 917 ," dapp "],
        [ 916 ," "],
        [ 914 ," dapp "],
        [ 913 ," Infra "],
        [ 912 ," Infra "],
        [ 911 ," "],
        [ 910 ," dapp "],
        [ 909 ," dapp "],
        [ 908 ," "],
        [ 906 ," "],
        [ 905 ," "],
        [ 904 ," "],
        [ 903 ," "],
        [ 902 ," "],
        [ 901 ," delete "],
        [ 900 ," dapp "],
        [ 899 ," dapp "],
        [ 898 ," dapp "],
        [ 897 ," dapp "],
        [ 896 ," dapp "],
        [ 895 ," delete "],
        [ 894 ," "],
        [ 893 ," delete "],
        [ 892 ," "],
        [ 891 ," dapp "],
        [ 890 ," "],
        [ 889 ," dapp "],
        [ 888 ," Infra "],
        [ 887 ," "],
        [ 886 ," "],
        [ 885 ," Infra "],
        [ 884 ," "],
        [ 883 ," "],
        [ 882 ," dapp "],
        [ 881 ," dapp "],
        [ 879 ," delete "],
        [ 878 ," dapp "],
        [ 877 ," "],
        [ 866 ," dapp "],
        [ 865 ," dapp "],
        [ 864 ," dapp "],
        [ 863 ," dapp "],
        [ 862 ," dapp "],
        [ 861 ," dapp "],
        [ 860 ," dapp "],
        [ 858 ," dapp "],
        [ 857 ," Community "],
        [ 855 ," Community "],
        [ 854 ," Infra "],
        [ 853 ," dapp "],
        [ 852 ," dapp "],
        [ 851 ," Community "],
        [ 850 ," Community "],
        [ 849 ," Infra "],
        [ 848 ," "],
        [ 846 ," dapp "],
        [ 845 ," Community "],
        [ 844 ," Infra "],
        [ 843 ," Infra "],
        [ 842 ," Infra "],
        [ 840 ," "],
        [ 837 ," dapp "],
        [ 836 ," "],
        [ 835 ," dapp "],
        [ 834 ," "],
        [ 833 ," dapp "],
        [ 832 ," dapp "],
        [ 831 ," "],
        [ 830 ," dapp "],
        [ 829 ," dapp "],
        [ 828 ," dapp "],
        [ 827 ," "],
        [ 826 ," dapp "],
        [ 825 ," dapp "],
        [ 824 ," dapp "],
        [ 823 ," "],
        [ 822 ," dapp "],
        [ 821 ," Infra "],
        [ 820 ," dapp "],
        [ 819 ," dapp "],
        [ 818 ," dapp "],
        [ 817 ," Infra "],
        [ 816 ," dapp "],
        [ 815 ," dapp "],
        [ 814 ," "],
        [ 813 ," "],
        [ 812 ," "],
        [ 811 ," "],
        [ 810 ," "],
        [ 809 ," "],
        [ 808 ," dapp "],
        [ 807 ," dapp "],
        [ 806 ," "],
        [ 805 ," "],
        [ 804 ," "],
        [ 803 ," dapp "],
        [ 802 ," Infra "],
        [ 801 ," Infra "],
        [ 799 ," Infra "],
        [ 798 ," Community "],
        [ 796 ," Infra "],
        [ 795 ," dapp "],
        [ 794 ," "],
        [ 793 ," "],
        [ 792 ," Community "],
        [ 789 ," "],
        [ 788 ," "],
        [ 787 ," dapp "],
        [ 785 ," "],
        [ 784 ," dapp "],
        [ 782 ," Community "],
        [ 781 ," Infra "],
        [ 780 ," dapp "],
        [ 779 ," "],
        [ 778 ," Infra "],
        [ 777 ," delete "],
        [ 776 ," delete "],
        [ 775 ," dapp "],
        [ 774 ," dapp "],
        [ 773 ," dapp "],
        [ 772 ," dapp "],
        [ 771 ," dapp "],
        [ 770 ," dapp "],
        [ 769 ," "],
        [ 768 ," Infra "],
        [ 767 ," dapp "],
        [ 766 ," "],
        [ 765 ," Infra "],
        [ 763 ," dapp "],
        [ 762 ," dapp "],
        [ 761 ," "],
        [ 760 ," "],
        [ 759 ," "],
        [ 758 ," "],
        [ 757 ," dapp "],
        [ 756 ," "],
        [ 755 ," dapp "],
        [ 749 ," delete "],
        [ 747 ," "],
        [ 746 ," "],
        [ 744 ," "],
        [ 743 ," "],
        [ 742 ," Community "],
        [ 741 ," dapp "],
        [ 740 ," "],
        [ 739 ," "],
        [ 738 ," "],
        [ 737 ," dapp "],
        [ 736 ," Infra "],
        [ 735 ," "],
        [ 734 ," "],
        [ 733 ," dapp "],
        [ 731 ," dapp "],
        [ 729 ," Infra "],
        [ 728 ," dapp "],
        [ 727 ," Community "],
        [ 724 ," dapp "],
        [ 723 ," dapp "],
        [ 722 ," Infra "],
        [ 720 ," "],
        [ 719 ," "],
        [ 718 ," dapp "],
        [ 717 ," "],
        [ 716 ," Infra "],
        [ 715 ," Community "],
        [ 714 ," dapp "],
        [ 711 ," dapp "],
        [ 710 ," "],
        [ 709 ," Community "],
        [ 708 ," Community "],
        [ 707 ," "],
        [ 706 ," "],
        [ 705 ," "],
        [ 704 ," "],
        [ 703 ," dapp "],
        [ 702 ," "],
        [ 701 ," "],
        [ 700 ," "],
        [ 699 ," "],
        [ 698 ," dapp "],
        [ 697 ," "],
        [ 696 ," "],
        [ 695 ," dapp "],
        [ 694 ," "],
        [ 693 ," dapp "],
        [ 692 ," "],
        [ 691 ," "],
        [ 690 ," dapp "],
        [ 689 ," dapp "],
        [ 688 ," dapp "],
        [ 687 ," dapp "],
        [ 686 ," "],
        [ 684 ," "],
        [ 683 ," "],
        [ 682 ," "],
        [ 681 ," dapp "],
        [ 680 ," dapp "],
        [ 679 ," "],
        [ 678 ," Infra "],
        [ 677 ," "],
        [ 676 ," dapp "],
        [ 675 ," "],
        [ 674 ," "],
        [ 673 ," dapp "],
        [ 672 ," Community "],
        [ 671 ," dapp "],
        [ 670 ," "],
        [ 668 ," Community "],
        [ 667 ," dapp "],
        [ 666 ," dapp "],
        [ 665 ," "],
        [ 664 ," delete "],
        [ 663 ," delete "],
        [ 662 ," "],
        [ 661 ," "],
        [ 660 ," dapp "],
        [ 659 ," dapp "],
        [ 658 ," dapp "],
        [ 656 ," "],
        [ 655 ," Community "],
        [ 654 ," "],
        [ 653 ," Infra "],
        [ 652 ," "],
        [ 651 ," dapp "],
        [ 650 ," dapp "],
        [ 648 ," delete "],
        [ 647 ," "],
        [ 646 ," Community "],
        [ 644 ," "],
        [ 643 ," "],
        [ 640 ," dapp "],
        [ 639 ," "],
        [ 638 ," dapp "],
        [ 637 ," dapp "],
        [ 636 ," "],
        [ 635 ," dapp "],
        [ 634 ," dapp "],
        [ 633 ," Infra "],
        [ 632 ," "],
        [ 631 ," "],
        [ 630 ," "],
        [ 629 ," Infra "],
        [ 628 ," Infra "],
        [ 627 ," dapp "],
        [ 626 ," dapp "],
        [ 624 ," dapp "],
        [ 623 ," Community "],
        [ 622 ," "],
        [ 621 ," "],
        [ 620 ," dapp "],
        [ 619 ," "],
        [ 618 ," dapp "],
        [ 617 ," "],
        [ 616 ," "],
        [ 615 ," "],
        [ 614 ," dapp "],
        [ 613 ," "],
        [ 612 ," "],
        [ 611 ," Community "],
        [ 610 ," dapp "],
        [ 609 ," dapp "],
        [ 608 ," Infra "],
        [ 607 ," "],
        [ 606 ," Community "],
        [ 605 ," Infra "],
        [ 604 ," dapp "],
        [ 603 ," "],
        [ 602 ," Community "],
        [ 601 ," dapp "],
        [ 600 ," dapp "],
        [ 599 ," Infra "],
        [ 598 ," "],
        [ 596 ," Infra "],
        [ 595 ," Infra "],
        [ 594 ," dapp "],
        [ 593 ," Infra "],
        [ 592 ," Infra "],
        [ 591 ," "],
        [ 590 ," Infra "],
        [ 589 ," "],
        [ 588 ," Infra "],
        [ 587 ," Community "],
        [ 586 ," Community "],
        [ 584 ," dapp "],
        [ 583 ," "],
        [ 582 ," "],
        [ 581 ," Infra "],
        [ 580 ," Infra "],
        [ 579 ," dapp "],
        [ 578 ," "],
        [ 575 ," Infra "],
        [ 573 ," dapp "],
        [ 572 ," "],
        [ 571 ," "],
        [ 570 ," delete "],
        [ 569 ," "],
        [ 568 ," "],
        [ 567 ," "],
        [ 566 ," "],
        [ 565 ," "],
        [ 564 ," dapp "],
        [ 563 ," Community "],
        [ 562 ," Community "],
        [ 561 ," "],
        [ 560 ," "],
        [ 559 ," "],
        [ 558 ," "],
        [ 557 ," dapp "],
        [ 556 ," dapp "],
        [ 555 ," dapp "],
        [ 554 ," Community "],
        [ 553 ," "],
        [ 552 ," Community "],
        [ 551 ," Infra "],
        [ 550 ," "],
        [ 549 ," "],
        [ 548 ," Community "],
        [ 547 ," "],
        [ 546 ," dapp "],
        [ 545 ," "],
        [ 544 ," dapp "],
        [ 543 ," Infra "],
        [ 542 ," "],
        [ 541 ," "],
        [ 540 ," Infra "],
        [ 539 ," dapp "],
        [ 538 ," "],
        [ 537 ," dapp "],
        [ 536 ," dapp "],
        [ 535 ," "],
        [ 534 ," "],
        [ 531 ," "],
        [ 530 ," dapp "],
        [ 529 ," "],
        [ 528 ," Infra "],
        [ 527 ," Infra "],
        [ 526 ," dapp "],
        [ 525 ," Community "],
        [ 524 ," dapp "],
        [ 523 ," "],
        [ 522 ," Community "],
        [ 520 ," "],
        [ 519 ," dapp "],
        [ 518 ," "],
        [ 517 ," "],
        [ 516 ," "],
        [ 515 ," dapp "],
        [ 514 ," dapp "],
        [ 513 ," dapp "],
        [ 512 ," dapp "],
        [ 511 ," dapp "],
        [ 510 ," dapp "],
        [ 509 ," dapp "],
        [ 508 ," Community "],
        [ 507 ," Community "],
        [ 506 ," "],
        [ 505 ," "],
        [ 504 ," "],
        [ 503 ," "],
        [ 502 ," "],
        [ 501 ," "],
        [ 498 ," "],
        [ 497 ," dapp "],
        [ 496 ," Infra "],
        [ 494 ," "],
        [ 493 ," "],
        [ 500 ," "],
        [ 491 ," dapp "],
        [ 490 ," dapp "],
        [ 489 ," "],
        [ 488 ," dapp "],
        [ 487 ," "],
        [ 486 ," dapp "],
        [ 485 ," "],
        [ 484 ," dapp "],
        [ 483 ," "],
        [ 482 ," "],
        [ 480 ," Infra "],
        [ 478 ," dapp "],
        [ 477 ," dapp "],
        [ 475 ," dapp "],
        [ 474 ," dapp "],
        [ 473 ," "],
        [ 472 ," "],
        [ 471 ," Infra "],
        [ 470 ," Infra "],
        [ 469 ," "],
        [ 468 ," Community "],
        [ 467 ," Community "],
        [ 466 ," "],
        [ 465 ," Community "],
        [ 464 ," dapp "],
        [ 463 ," "],
        [ 462 ," dapp "],
        [ 461 ," dapp "],
        [ 460 ," "],
        [ 459 ," dapp "],
        [ 457 ," dapp "],
        [ 456 ," "],
        [ 455 ," dapp "],
        [ 454 ," "],
        [ 453 ," Infra "],
        [ 452 ," dapp "],
        [ 451 ," dapp "],
        [ 450 ," Infra "],
        [ 449 ," Community "],
        [ 448 ," delete "],
        [ 447 ," dapp "],
        [ 446 ," dapp "],
        [ 445 ," dapp "],
        [ 444 ," Infra "],
        [ 443 ," dapp "],
        [ 442 ," dapp "],
        [ 441 ," dapp "],
        [ 438 ," dapp "],
        [ 437 ," "],
        [ 433 ," Community "],
        [ 429 ," dapp "],
        [ 428 ," Community "],
        [ 427 ," Community "],
        [ 426 ," dapp "],
        [ 425 ," Community "],
        [ 420 ," dapp "],
        [ 419 ," dapp "],
        [ 417 ," dapp "],
        [ 416 ," dapp "],
        [ 414 ," dapp "],
        [ 413 ," Infra "],
        [ 412 ," Infra "],
        [ 410 ," Community "],
        [ 408 ," dapp "],
        [ 407 ," Community "],
        [ 406 ," dapp "],
        [ 405 ," "],
        [ 404 ," "],
        [ 403 ," dapp "],
        [ 401 ," Infra "],
        [ 400 ," dapp "],
        [ 398 ," dapp "],
        [ 397 ," dapp "],
        [ 396 ," dapp "],
        [ 395 ," dapp "],
        [ 394 ," dapp "],
        [ 392 ," "],
        [ 391 ," dapp "],
        [ 390 ," Infra "],
        [ 389 ," dapp "],
        [ 388 ," Community "],
        [ 387 ," dapp "],
        [ 386 ," "],
        [ 385 ," Infra "],
        [ 384 ," Infra "],
        [ 383 ," Infra "],
        [ 382 ," Infra "],
        [ 381 ," dapp "],
        [ 380 ," "],
        [ 379 ," dapp "],
        [ 378 ," dapp "],
        [ 377 ," dapp "],
        [ 375 ," dapp "],
        [ 374 ," "],
        [ 373 ," Infra "],
        [ 372 ," "],
        [ 371 ," "],
        [ 370 ," Infra "],
        [ 369 ," dapp "],
        [ 368 ," Community "],
        [ 366 ," "],
        [ 365 ," dapp "],
        [ 363 ," Infra "],
        [ 362 ," "],
        [ 361 ," Community "],
        [ 360 ," Community "],
        [ 359 ," dapp "],
        [ 358 ," Infra "],
        [ 357 ," delete "],
        [ 356 ," dapp "],
        [ 354 ," Community "],
        [ 353 ," dapp "],
        [ 352 ," "],
        [ 351 ," dapp "],
        [ 350 ," dapp "],
        [ 349 ," delete "],
        [ 348 ," dapp "],
        [ 347 ," Infra "],
        [ 345 ," "],
        [ 344 ," dapp "],
        [ 343 ," Infra "],
        [ 342 ," Infra "],
        [ 341 ," dapp "],
        [ 339 ," Infra "],
        [ 338 ," Infra "],
        [ 337 ," Infra "],
        [ 336 ," Community "],
        [ 335 ," dapp "],
        [ 334 ," Infra "],
        [ 332 ," "],
        [ 331 ," Infra "],
        [ 330 ," dapp "],
        [ 329 ," "],
        [ 328 ," dapp "],
        [ 327 ," dapp "],
        [ 325 ," Community "],
        [ 324 ," "],
        [ 323 ," Infra "],
        [ 322 ," Community "],
        [ 321 ," dapp "],
        [ 320 ," dapp "],
        [ 318 ," dapp "],
        [ 317 ," dapp "],
        [ 316 ," "],
        [ 315 ," dapp "],
        [ 314 ," "],
        [ 313 ," Community "],
        [ 312 ," dapp "],
        [ 311 ," dapp "],
        [ 310 ," health "],
        [ 309 ," "],
        [ 308 ," Infra "],
        [ 307 ," dapp "],
        [ 306 ," dapp "],
        [ 305 ," "],
        [ 304 ," Community "],
        [ 303 ," dapp "],
        [ 300 ," dapp "],
        [ 297 ," dapp "],
        [ 296 ," Community "],
        [ 295 ," dapp "],
        [ 294 ," Community "],
        [ 293 ," Community "],
        [ 292 ," Community "],
        [ 290 ," Infra "],
        [ 289 ," "],
        [ 288 ," Community "],
        [ 287 ," dapp "],
        [ 286 ," Community "],
        [ 285 ," dapp "],
        [ 284 ," Infra "],
        [ 283 ," dapp "],
        [ 282 ," Infra "],
        [ 281 ," dapp "],
        [ 280 ," dapp "],
        [ 279 ," "],
        [ 278 ," "],
        [ 277 ," dapp "],
        [ 276 ," dapp "],
        [ 275 ," Infra "],
        [ 274 ," Infra "],
        [ 273 ," Infra "],
        [ 272 ," Community "],
        [ 271 ," Infra "],
        [ 270 ," dapp "],
        [ 269 ," dapp "],
        [ 268 ," dapp "],
        [ 267 ," dapp "],
        [ 266 ," dapp "],
        [ 265 ," dapp "],
        [ 264 ," dapp "],
        [ 263 ," dapp "],
        [ 262 ," dapp "],
        [ 261 ," Infra "],
        [ 260 ," "],
        [ 259 ," "],
        [ 258 ," Infra "],
        [ 257 ," dapp "],
        [ 256 ," dapp "],
        [ 255 ," dapp "],
        [ 254 ," dapp "],
        [ 253 ," dapp "],
        [ 252 ," dapp "],
        [ 251 ," "],
        [ 250 ," "],
        [ 249 ," dapp "],
        [ 248 ," Infra "],
        [ 247 ," Community "],
        [ 246 ," dapp "],
        [ 242 ," delete "],
        [ 241 ," dapp "],
        [ 240 ," Community "],
        [ 239 ," "],
        [ 238 ," "],
        [ 237 ," "],
        [ 236 ," "],
        [ 235 ," dapp "],
        [ 234 ," Infra "],
        [ 233 ," Infra "],
        [ 232 ," Infra "],
        [ 231 ," "],
        [ 229 ," dapp "],
        [ 228 ," Community "],
        [ 227 ," Infra "],
        [ 226 ," dapp "],
        [ 225 ," dapp "],
        [ 224 ," Infra "],
        [ 223 ," "],
        [ 222 ," Infra "],
        [ 221 ," dapp "],
        [ 220 ," "],
        [ 219 ," dapp "],
        [ 218 ," Infra "],
        [ 217 ," dapp "],
        [ 216 ," dapp "],
        [ 215 ," "],
        [ 213 ," dapp "],
        [ 212 ," dapp "],
        [ 211 ," "],
        [ 210 ," delete "],
        [ 209 ," "],
        [ 207 ," dapp "],
        [ 206 ," dapp "],
        [ 205 ," "],
        [ 204 ," "],
        [ 203 ," "],
        [ 202 ," Infra "],
        [ 201 ," "],
        [ 200 ," Infra "],
        [ 199 ," Infra "],
        [ 198 ," dapp "],
        [ 197 ," Infra "],
        [ 196 ," dapp "],
        [ 195 ," "],
        [ 194 ," dapp "],
        [ 193 ," dapp "],
        [ 192 ," dapp "],
        [ 191 ," dapp "],
        [ 190 ," dapp "],
        [ 189 ," dapp "],
        [ 188 ," Infra "],
        [ 187 ," Infra "],
        [ 186 ," dapp "],
        [ 185 ," dapp "],
        [ 184 ," Infra "],
        [ 183 ," dapp "],
        [ 181 ," dapp "],
        [ 180 ," dapp "],
        [ 179 ," Infra "],
        [ 178 ," Infra "],
        [ 177 ," dapp "],
        [ 175 ," "],
        [ 173 ," dapp "],
        [ 172 ," dapp "],
        [ 171 ," dapp "],
        [ 170 ," Infra "],
        [ 169 ," dapp "],
        [ 167 ," dapp "],
        [ 166 ," delete "],
        [ 165 ," dapp "],
        [ 164 ," dapp "],
        [ 163 ," dapp "],
        [ 161 ," dapp "],
        [ 160 ," "],
        [ 159 ," dapp "],
        [ 158 ," dapp "],
        [ 156 ," "],
        [ 155 ," dapp "],
        [ 153 ," dapp "],
        [ 152 ," "],
        [ 151 ," delete "],
        [ 150 ," dapp "],
        [ 149 ," dapp "],
        [ 148 ," delete "],
        [ 147 ," Infra "],
        [ 146 ," Infra "],
        [ 145 ," Infra "],
        [ 144 ," Community "],
        [ 143 ," Infra "],
        [ 142 ," Infra "],
        [ 141 ," dapp "],
        [ 139 ," Community "],
        [ 138 ," dapp "],
        [ 137 ," Infra "],
        [ 135 ," dapp "],
        [ 134 ," dapp "],
        [ 132 ," Infra "],
        [ 131 ," Infra "],
        [ 130 ," "],
        [ 127 ," Community "],
        [ 126 ," Community "],
        [ 123 ," Community "],
        [ 122 ," Community "],
        [ 121 ," delete "],
        [ 120 ," Infra "],
        [ 118 ," health "],
        [ 117 ," Infra "],
        [ 116 ," "],
        [ 115 ," delete "],
        [ 114 ," dapp "],
        [ 113 ," Infra "],
        [ 112 ," "],
        [ 111 ," Infra "],
        [ 110 ," delete "],
        [ 108 ," Infra "],
        [ 107 ," Infra "],
        [ 106 ," Infra "],
        [ 105 ," Infra "],
        [ 104 ," Community "],
        [ 103 ," Community "],
        [ 102 ," Infra "],
        [ 101 ," dapp "],
        [ 99 ," Infra "],
        [ 97 ," dapp "],
        [ 96 ," dapp "],
        [ 95 ," Infra "],
        [ 94 ," Infra "],
        [ 93 ," delete "],
        [ 91 ," dapp "],
        [ 90 ," dapp "],
        [ 87 ," dapp "],
        [ 85 ," Infra "],
        [ 83 ," Community "],
        [ 81 ," Community "],
        [ 79 ," Infra "],
        [ 78 ," delete "],
        [ 76 ," Community "],
        [ 75 ," Community "],
        [ 74 ," "],
        [ 73 ," Community "],
        [ 72 ," Community "],
        [ 66 ," Infra "],
        [ 65 ," Infra "],
        [ 63 ," "],
        [ 62 ," Infra "],
        [ 58 ," Infra "],
        [ 56 ," Community "],
        [ 55 ," Infra "],
        [ 54 ," Infra "],
        [ 49 ," "],
        [ 44 ," Infra "],
        [ 40 ," "],
        [ 39 ," Infra "],
        [ 38 ," "],
        [ 37 ," Infra "],
        [ 36 ," Community "],
        [ 32 ," Infra "],
        [ 31 ," Community "],
        [ 30 ," "],
        [ 29 ," Infra "],
        [ 26 ," dapp "],
        [ 25 ," Infra "],
        [ 24 ," Infra "],
        [ 22 ," Infra "],
        [ 20 ," dapp "],
        [ 19 ," Infra "],
        [ 18 ," Infra "],
        [ 17 ," Infra "],
        [ 16 ," Community "],
        [ 15 ," Infra "],
        [ 13 ," Infra "],
        [ 12 ," Infra "],
        [ 9 ," Infra "],
        [ 7 ," Community "],

        ]

        for ele in data:
            try:
                #print(ele[0])
                grant = Grant.objects.get(pk=ele[0])
                if not ele[1].strip().lower():
                    #print('noop')
                    pass
                if ele[1].strip().lower() == 'infra':
                    grant.grant_type = GrantType.objects.get(name='infra_tech')
                    #print(ele[1].strip().lower())
                elif ele[1].strip().lower() == 'dapp':
                    grant.grant_type = GrantType.objects.get(name='tech')
                    #print(ele[1].strip().lower())
                elif ele[1].strip().lower() == 'community':
                    grant.grant_type = GrantType.objects.get(name='media')
                    #print(ele[1].strip().lower())
                elif ele[1].strip().lower() == 'matic':
                    grant.grant_type = GrantType.objects.get(name='matic')
                    #print(ele[1].strip().lower())
                elif ele[1].strip().lower() == 'health':
                    grant.grant_type = GrantType.objects.get(name='health')
                    #print(ele[1].strip().lower())
                elif ele[1].strip().lower() == 'change':
                    grant.grant_type = GrantType.objects.get(name='change')
                    #print(ele[1].strip().lower())
                elif ele[1].strip().lower() == 'delete':
                    grant.hidden = True
                    grant.active = True
                    #print(ele[1].strip().lower())
                else:
                    #print(ele[1].strip().lower())
                    if ele[1].strip().lower():
                        raise e

                needs_subcategory_reclass = not grant.grant_type.categories.all().filter(pk__in=grant.categories.all()).exists()
                if not needs_subcategory_reclass:
                    #print(ele[0])
                    grant.categories.set(grant.grant_type.categories.all())

                grant.save()
            except Exception as e:
                print("*****************************")
                print(f"******DERP {ele[0]} {ele[1].strip().lower()} *****")
                print(f"******DERP {e}")
                print("*****************************")

