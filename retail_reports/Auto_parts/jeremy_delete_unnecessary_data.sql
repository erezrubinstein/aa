use retaildb_timeseries_auto_parts_v5_shrunken
go

declare @threshold_id int = 5 -- set for file miles

-- find all trade areas with this threshold id
declare @trade_areas table (trade_area_id int primary key)
insert into @trade_areas
select trade_area_id from trade_areas where threshold_id <> @threshold_id

-- delete all data associated with these trade areas
/*
delete from demographic_numvalues where trade_area_id in (select trade_area_id from @trade_areas)
delete from demographic_strvalues where trade_area_id in (select trade_area_id from @trade_areas)
delete from monopolies where trade_area_id in (select trade_area_id from @trade_areas)
delete from trade_area_shapes where trade_area_id in (select trade_area_id from @trade_areas)
delete from competitive_stores where trade_area_id in (select trade_area_id from @trade_areas)
delete from trade_area_analytics where trade_area_id in (select trade_area_id from @trade_areas)
delete from trade_areas where trade_area_id in (select trade_area_id from @trade_areas)
*/




-- declare data items that you want to keep
declare @date_items_keep table (data_item_id int primary key)
insert into @date_items_keep
select 13 UNION
select 16 UNION
select 31 UNION
select 48 UNION
select 52 UNION
select 56 UNION
select 60 UNION
select 64 UNION
select 68 UNION
select 72 UNION
select 76 UNION
select 80 UNION
select 84 UNION
select 88 UNION
select 261 UNION
select 600 UNION
select 603 UNION
select 606 UNION
select 609 UNION
select 612 UNION
select 615 UNION
select 618 UNION
select 621 UNION
select 624 UNION
select 627 UNION
select 630 UNION
select 633 UNION
select 636 UNION
select 647 UNION
select 648 UNION
select 651 UNION
select 652 UNION
select 653 UNION
select 654 UNION
select 655 UNION
select 658 UNION
select 659 UNION
select 660 UNION
select 661 UNION
select 662 UNION
select 665 UNION
select 666 UNION
select 667 UNION
select 668 UNION
select 669 UNION
select 672 UNION
select 673 UNION
select 674 UNION
select 675 UNION
select 676 UNION
select 679 UNION
select 680 UNION
select 681 UNION
select 682 UNION
select 683 UNION
select 686 UNION
select 687 UNION
select 688 UNION
select 689 UNION
select 690 UNION
select 693 UNION
select 694 UNION
select 695 UNION
select 696 UNION
select 697 UNION
select 700 UNION
select 701 UNION
select 702 UNION
select 703 UNION
select 704 UNION
select 707 UNION
select 708 UNION
select 709 UNION
select 710 UNION
select 711 UNION
select 714 UNION
select 715 UNION
select 716 UNION
select 717 UNION
select 718 UNION
select 721 UNION
select 722 UNION
select 723 UNION
select 724 UNION
select 725 UNION
select 728 UNION
select 729 UNION
select 730 UNION
select 731 UNION
select 732 UNION
select 735 UNION
select 736 UNION
select 737 UNION
select 738 UNION
select 739 UNION
select 742 UNION
select 743 UNION
select 744 UNION
select 745 UNION
select 746 UNION
select 749 UNION
select 750 UNION
select 751 UNION
select 752 UNION
select 753 UNION
select 756 UNION
select 757 UNION
select 758 UNION
select 759 UNION
select 760 UNION
select 763 UNION
select 764 UNION
select 765 UNION
select 766 UNION
select 767 UNION
select 770 UNION
select 771 UNION
select 772 UNION
select 773 UNION
select 774 UNION
select 777 UNION
select 778 UNION
select 779 UNION
select 780 UNION
select 781 UNION
select 784 UNION
select 785 UNION
select 786 UNION
select 787 UNION
select 788 UNION
select 791 UNION
select 792 UNION
select 793 UNION
select 794 UNION
select 795 UNION
select 798 UNION
select 799 UNION
select 800 UNION
select 801 UNION
select 802 UNION
select 805 UNION
select 806 UNION
select 807 UNION
select 808 UNION
select 809 UNION
select 812 UNION
select 813 UNION
select 814 UNION
select 815 UNION
select 816 UNION
select 819 UNION
select 820 UNION
select 821 UNION
select 822 UNION
select 823 UNION
select 826 UNION
select 827 UNION
select 828 UNION
select 829 UNION
select 830 UNION
select 833 UNION
select 834 UNION
select 835 UNION
select 836 UNION
select 837 UNION
select 840 UNION
select 841 UNION
select 842 UNION
select 843 UNION
select 844 UNION
select 847 UNION
select 848 UNION
select 849 UNION
select 850 UNION
select 851 UNION
select 854 UNION
select 855 UNION
select 856 UNION
select 1247 UNION
select 1250 UNION
select 1253 UNION
select 1256 UNION
select 1259 UNION
select 1262 UNION
select 1265 UNION
select 1268 UNION
select 1271 UNION
select 1274 UNION
select 1277 UNION
select 1280 UNION
select 1283 UNION
select 1286 UNION
select 1289 UNION
select 1292 UNION
select 1295 UNION
select 1298 UNION
select 1301 UNION
select 1304 UNION
select 1307 UNION
select 1310 UNION
select 1313 UNION
select 1316 UNION
select 1319 UNION
select 1322 UNION
select 1325 UNION
select 1328 UNION
select 859 UNION
select 862 UNION
select 865 UNION
select 868 UNION
select 871 UNION
select 874 UNION
select 877 UNION
select 880 UNION
select 883 UNION
select 886 UNION
select 889 UNION
select 892 UNION
select 895 UNION
select 898 UNION
select 901 UNION
select 904 UNION
select 907 UNION
select 910 UNION
select 913 UNION
select 916 UNION
select 919 UNION
select 922 UNION
select 925 UNION
select 928 UNION
select 931


-- get data items to delete
declare @date_items_delete table (data_item_id int primary key)
insert into @date_items_delete
select data_item_id from data_items where data_item_id not in (select data_item_id from @date_items_keep)

-- delete all demographics, which are not in this set


/*
delete top(10000000) from demographic_numvalues where data_item_id in (select data_item_id from @date_items_delete)
delete top(10000000) from demographic_strvalues where data_item_id in (select data_item_id from @date_items_delete)
*/

declare @companies_to_delete_competitions_from table(company_id int primary key)
insert into @companies_to_delete_competitions_from
select company_id
from companies
where name in ('New Auto Dealers', 'Fast Lube & Oil Change Stores', 'Tires')

/*
delete cs
from competitive_stores cs
inner join stores home on home.store_id = cs.home_store_id
inner join stores away on away.store_id = cs.away_store_id
where home.company_id in (select company_id from @companies_to_delete_competitions_from)
*/